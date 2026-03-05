"""GLPI REST API client — session management, CRUD, and search operations.

Usage::

    from glpi_toolkit.core.glpi_client import GLPIClient

    client = GLPIClient(
        url="http://glpi.example.com",
        api_token="your_user_api_token",
        app_token="your_application_token",
    )
    with client:
        tickets = client.get_items("Ticket", range_="0-50")
        new_id = client.create_item("Ticket", {"name": "Test", "content": "Body"})

The client authenticates via ``api_token`` (user token) + ``app_token``
(registered application token in GLPI's API settings).
"""

from __future__ import annotations

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class GLPIError(Exception):
    """Base exception for GLPI API errors."""

    def __init__(self, message: str, status_code: int | None = None, response_body: Any = None) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)


class GLPIAuthError(GLPIError):
    """Raised when authentication / session initialization fails."""


class GLPINotFoundError(GLPIError):
    """Raised when a requested item does not exist (HTTP 404)."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class GLPIClient:
    """Thin wrapper around the GLPI REST API.

    Parameters
    ----------
    url:
        Base URL of the GLPI instance (e.g. ``http://192.168.1.50``).
        A trailing ``/apirest.php`` is appended automatically.
    api_token:
        User API token (generated in *User preferences > Remote access keys*).
    app_token:
        Application token (registered in *Setup > General > API*).
    verify_ssl:
        Whether to verify TLS certificates.  Defaults to ``True``.
    timeout:
        Request timeout in seconds.  Defaults to ``30``.
    """

    def __init__(
        self,
        url: str,
        api_token: str,
        app_token: str = "",
        *,
        verify_ssl: bool = True,
        timeout: int = 30,
    ) -> None:
        self.base_url = url.rstrip("/")
        if not self.base_url.endswith("/apirest.php"):
            self.base_url += "/apirest.php"

        self.api_token = api_token
        self.app_token = app_token
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        self._session_token: str | None = None
        self._http = requests.Session()
        self._http.verify = self.verify_ssl

    # -- context manager ----------------------------------------------------

    def __enter__(self) -> GLPIClient:
        self.init_session()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.kill_session()

    # -- helpers ------------------------------------------------------------

    def _headers(self) -> dict[str, str]:
        """Build the common header dict for every request."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
        }
        if self.app_token:
            headers["App-Token"] = self.app_token
        if self._session_token:
            headers["Session-Token"] = self._session_token
        return headers

    def _auth_headers(self) -> dict[str, str]:
        """Headers for the ``initSession`` call (uses ``Authorization``)."""
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Authorization": f"user_token {self.api_token}",
        }
        if self.app_token:
            headers["App-Token"] = self.app_token
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
    ) -> Any:
        """Execute an HTTP request and return the parsed JSON response.

        Raises
        ------
        GLPIAuthError
            On 401 responses.
        GLPINotFoundError
            On 404 responses.
        GLPIError
            On any other non-2xx response.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.debug("%s %s params=%s", method, url, params)

        response = self._http.request(
            method,
            url,
            headers=self._headers(),
            params=params,
            json=json_body,
            timeout=self.timeout,
        )

        if response.status_code == 401:
            raise GLPIAuthError(
                "Authentication failed — check api_token and app_token",
                status_code=401,
                response_body=response.text,
            )

        if response.status_code == 404:
            raise GLPINotFoundError(
                f"Item not found: {endpoint}",
                status_code=404,
                response_body=response.text,
            )

        if response.status_code == 204:
            # No content (e.g. successful DELETE)
            return None

        if not response.ok:
            body = None
            try:
                body = response.json()
            except ValueError:
                body = response.text
            raise GLPIError(
                f"GLPI API error (HTTP {response.status_code}): {body}",
                status_code=response.status_code,
                response_body=body,
            )

        # Some endpoints return empty body on success
        if not response.content:
            return None

        return response.json()

    # -- session management -------------------------------------------------

    def init_session(self) -> str:
        """Open an API session and store the session token.

        Returns
        -------
        str
            The session token.
        """
        url = f"{self.base_url}/initSession"
        logger.info("Initializing GLPI session at %s", self.base_url)

        resp = self._http.get(
            url,
            headers=self._auth_headers(),
            timeout=self.timeout,
        )

        if not resp.ok:
            raise GLPIAuthError(
                f"Failed to init session (HTTP {resp.status_code}): {resp.text}",
                status_code=resp.status_code,
                response_body=resp.text,
            )

        data = resp.json()
        self._session_token = data.get("session_token", "")
        if not self._session_token:
            raise GLPIAuthError(
                "No session_token in response",
                response_body=data,
            )
        logger.info("GLPI session initialized successfully")
        return self._session_token

    def kill_session(self) -> None:
        """Close the current API session."""
        if not self._session_token:
            return
        try:
            url = f"{self.base_url}/killSession"
            self._http.get(url, headers=self._headers(), timeout=self.timeout)
            logger.info("GLPI session closed")
        except requests.RequestException as exc:
            logger.warning("Failed to close GLPI session: %s", exc)
        finally:
            self._session_token = None

    @property
    def is_authenticated(self) -> bool:
        """Return ``True`` if a session token is active."""
        return self._session_token is not None

    # -- CRUD operations ----------------------------------------------------

    def get_items(
        self,
        item_type: str,
        *,
        range_: str = "0-50",
        sort: int | None = None,
        order: str = "ASC",
        expand_dropdowns: bool = False,
        only_id: bool = False,
        search_criteria: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve a list of items of the given type.

        Parameters
        ----------
        item_type:
            GLPI item type (e.g. ``"Ticket"``, ``"Computer"``).
        range_:
            Pagination range (e.g. ``"0-50"``).
        sort:
            Field ID to sort by.
        order:
            Sort direction: ``"ASC"`` or ``"DESC"``.
        expand_dropdowns:
            Resolve dropdown IDs to their display values.
        only_id:
            Return only ``id`` fields (lighter response).
        search_criteria:
            Additional filter criteria as a dict.

        Returns
        -------
        list[dict]
            List of item dicts.
        """
        params: dict[str, Any] = {"range": range_, "order": order}
        if sort is not None:
            params["sort"] = sort
        if expand_dropdowns:
            params["expand_dropdowns"] = "true"
        if only_id:
            params["only_id"] = "true"
        if search_criteria:
            params.update(search_criteria)

        result = self._request("GET", item_type, params=params)
        if isinstance(result, list):
            return result
        return []

    def get_item(
        self,
        item_type: str,
        item_id: int,
        *,
        expand_dropdowns: bool = False,
    ) -> dict[str, Any]:
        """Retrieve a single item by ID.

        Parameters
        ----------
        item_type:
            GLPI item type.
        item_id:
            Numeric ID of the item.
        expand_dropdowns:
            Resolve dropdown IDs to display values.

        Returns
        -------
        dict
            The item data.
        """
        params: dict[str, Any] = {}
        if expand_dropdowns:
            params["expand_dropdowns"] = "true"

        result = self._request("GET", f"{item_type}/{item_id}", params=params)
        return result if isinstance(result, dict) else {}

    def create_item(
        self,
        item_type: str,
        payload: dict[str, Any],
    ) -> int:
        """Create a new item.

        Parameters
        ----------
        item_type:
            GLPI item type.
        payload:
            Field-value pairs for the new item.

        Returns
        -------
        int
            ID of the newly created item.
        """
        body = {"input": payload}
        result = self._request("POST", item_type, json_body=body)

        if isinstance(result, dict):
            return int(result.get("id", 0))
        if isinstance(result, list) and result:
            return int(result[0].get("id", 0))
        return 0

    def create_items(
        self,
        item_type: str,
        payloads: list[dict[str, Any]],
    ) -> list[int]:
        """Create multiple items in a single request.

        Parameters
        ----------
        item_type:
            GLPI item type.
        payloads:
            List of field-value dicts, one per item.

        Returns
        -------
        list[int]
            IDs of the newly created items.
        """
        body = {"input": payloads}
        result = self._request("POST", item_type, json_body=body)

        if isinstance(result, list):
            return [int(item.get("id", 0)) for item in result if isinstance(item, dict)]
        return []

    def update_item(
        self,
        item_type: str,
        item_id: int,
        payload: dict[str, Any],
    ) -> bool:
        """Update an existing item.

        Parameters
        ----------
        item_type:
            GLPI item type.
        item_id:
            Numeric ID of the item to update.
        payload:
            Field-value pairs to update.

        Returns
        -------
        bool
            ``True`` if the update succeeded.
        """
        payload["id"] = item_id
        body = {"input": payload}
        result = self._request("PUT", item_type, json_body=body)

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                return bool(first.get(str(item_id), False))
        return result is not None

    def delete_item(
        self,
        item_type: str,
        item_id: int,
        *,
        force_purge: bool = False,
    ) -> bool:
        """Delete (or purge) an item.

        Parameters
        ----------
        item_type:
            GLPI item type.
        item_id:
            Numeric ID of the item.
        force_purge:
            If ``True``, permanently remove instead of moving to trash.

        Returns
        -------
        bool
            ``True`` if deletion succeeded.
        """
        body: dict[str, Any] = {"input": {"id": item_id}}
        if force_purge:
            body["force_purge"] = True
        result = self._request("DELETE", item_type, json_body=body)

        if isinstance(result, list) and result:
            first = result[0]
            if isinstance(first, dict):
                return bool(first.get(str(item_id), False))
        return result is None  # 204 No Content

    # -- search -------------------------------------------------------------

    def search(
        self,
        item_type: str,
        criteria: list[dict[str, Any]],
        *,
        range_: str = "0-50",
        forcedisplay: list[int] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a GLPI search query.

        Parameters
        ----------
        item_type:
            GLPI item type to search.
        criteria:
            List of search criteria dicts.  Each dict should have:
            ``field``, ``searchtype``, ``value``, and optionally ``link``.
        range_:
            Pagination range.
        forcedisplay:
            List of field IDs to include in the response.

        Returns
        -------
        list[dict]
            Matching items (from ``response.data`` in GLPI's format).
        """
        params: dict[str, Any] = {"range": range_}

        for idx, criterion in enumerate(criteria):
            for key, value in criterion.items():
                params[f"criteria[{idx}][{key}]"] = value

        if forcedisplay:
            for idx, field_id in enumerate(forcedisplay):
                params[f"forcedisplay[{idx}]"] = field_id

        result = self._request("GET", f"search/{item_type}", params=params)

        if isinstance(result, dict):
            return result.get("data", [])
        return []

    # -- convenience --------------------------------------------------------

    def get_full_session(self) -> dict[str, Any]:
        """Return full session info (current user, profile, entity, etc.)."""
        result = self._request("GET", "getFullSession")
        return result.get("session", result) if isinstance(result, dict) else {}

    def get_active_profile(self) -> dict[str, Any]:
        """Return the active user profile."""
        result = self._request("GET", "getActiveProfile")
        return result if isinstance(result, dict) else {}

    def get_my_entities(self) -> list[dict[str, Any]]:
        """Return entities accessible by the current session."""
        result = self._request("GET", "getMyEntities")
        if isinstance(result, dict):
            return result.get("myentities", [])
        return result if isinstance(result, list) else []
