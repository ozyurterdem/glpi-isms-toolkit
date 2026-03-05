"""Core module — configuration loading, GLPI API client, and shared exceptions."""

from glpi_toolkit.core.config import (
    CompanyConfig,
    SLAConfig,
    SecurityConfig,
    ToolkitConfig,
    load_config,
)
from glpi_toolkit.core.glpi_client import (
    GLPIAuthError,
    GLPIClient,
    GLPIError,
    GLPINotFoundError,
)

__all__ = [
    "ToolkitConfig",
    "load_config",
    "CompanyConfig",
    "SLAConfig",
    "SecurityConfig",
    "GLPIClient",
    "GLPIError",
    "GLPIAuthError",
    "GLPINotFoundError",
]
