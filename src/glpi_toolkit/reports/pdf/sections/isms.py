"""ISMS integration section — documents, password policy, RBAC, lifecycle."""

from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.styles import ReportStyles

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class ISMSSection:
    """Renders the ISMS integration section."""

    def __init__(
        self,
        config: dict[str, Any],
        styles: ReportStyles,
        strings: dict[str, str],
    ) -> None:
        self.config = config
        self.styles = styles
        self.s = strings

    def _document_categories(self) -> list[Flowable]:
        st = self.styles.get_styles()
        assets_cfg = self.config.get("assets", {})
        doc_cats: list[str] = assets_cfg.get("document_categories", [])
        isms_docs = [c for c in doc_cats if "ISMS" in c or "Audit" in c or "Procedure" in c]
        other_docs = [c for c in doc_cats if c not in isms_docs]

        elements: list[Flowable] = [
            Paragraph(self.s.get("isms_docs_title", ""), st["SubSection"]),
            Paragraph(self.s.get("isms_docs_body", ""), st["BodyText2"]),
        ]
        for doc in isms_docs:
            elements.append(Paragraph(f"\u2022 {doc}", st["BulletItem"]))
        if other_docs:
            elements.append(Spacer(1, 4))
            elements.append(
                Paragraph(self.s.get("isms_docs_other", ""), st["BodyText2"])
            )
            for doc in other_docs:
                elements.append(Paragraph(f"\u2022 {doc}", st["BulletItem"]))
        elements.append(Spacer(1, 12))
        return elements

    def _password_policy(self) -> list[Flowable]:
        st = self.styles.get_styles()
        sec = self.config.get("security", {})
        pwd = sec.get("password_policy", {})
        lockout = sec.get("account_lockout", {})

        header = [self.s.get("isms_pwd_setting", ""), self.s.get("isms_pwd_value", "")]
        rows: list[list[str]] = [header]
        field_map = [
            ("isms_pwd_min_length", str(pwd.get("min_length", ""))),
            ("isms_pwd_uppercase", self._yesno(pwd.get("require_uppercase"))),
            ("isms_pwd_lowercase", self._yesno(pwd.get("require_lowercase"))),
            ("isms_pwd_number", self._yesno(pwd.get("require_number"))),
            ("isms_pwd_symbol", self._yesno(pwd.get("require_symbol"))),
            ("isms_pwd_expiry", f'{pwd.get("expiry_days", "")} {self.s.get("days", "")}'),
            ("isms_pwd_max_attempts", str(lockout.get("max_attempts", ""))),
            ("isms_pwd_lockout", f'{lockout.get("lockout_minutes", "")} {self.s.get("minutes", "")}'),
        ]
        for key, val in field_map:
            rows.append([self.s.get(key, key), val])

        return [
            Paragraph(self.s.get("isms_pwd_title", ""), st["SubSection"]),
            Paragraph(self.s.get("isms_pwd_body", ""), st["BodyText2"]),
            Paragraph(
                self.s.get("isms_pwd_ref", ""),
                st["ISORef"],
            ),
            make_table(rows, [USABLE * 0.55, USABLE * 0.45], report_colors=self.styles.colors),
            Spacer(1, 12),
        ]

    def _rbac_profiles(self) -> list[Flowable]:
        st = self.styles.get_styles()
        profiles: list[dict[str, Any]] = self.config.get("security", {}).get("profiles", [])
        header = [
            self.s.get("isms_rbac_role", ""),
            self.s.get("isms_rbac_desc", ""),
            self.s.get("isms_rbac_tickets", ""),
            self.s.get("isms_rbac_admin", ""),
        ]
        rows: list[list[str]] = [header]
        for p in profiles:
            perms = p.get("permissions", {})
            rows.append([
                p.get("name", ""),
                p.get("description", ""),
                perms.get("tickets", ""),
                self._yesno(perms.get("admin")),
            ])

        return [
            Paragraph(self.s.get("isms_rbac_title", ""), st["SubSection"]),
            Paragraph(self.s.get("isms_rbac_body", ""), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.15, USABLE * 0.40, USABLE * 0.20, USABLE * 0.25],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _lifecycle(self) -> list[Flowable]:
        st = self.styles.get_styles()
        templates: list[dict[str, Any]] = self.config.get("templates", [])
        lifecycle_tpls = [t for t in templates if t.get("isms_ref") == "ISMS-PRO-002"]

        elements: list[Flowable] = [
            Paragraph(self.s.get("isms_lifecycle_title", ""), st["SubSection"]),
            Paragraph(self.s.get("isms_lifecycle_body", ""), st["BodyText2"]),
        ]
        for tpl in lifecycle_tpls:
            name = tpl.get("name", "")
            checklist: list[str] = tpl.get("checklist", [])
            elements.append(Paragraph(f"<b>{name}</b>", st["BodyText2"]))
            for item in checklist:
                elements.append(Paragraph(f"\u2022 {item}", st["BulletItem"]))
            elements.append(Spacer(1, 6))

        return elements

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _yesno(val: Any) -> str:
        if val is True:
            return "\u2713"
        if val is False:
            return "\u2717"
        return str(val) if val is not None else ""

    # ── Public API ───────────────────────────────────────────────

    def render(self) -> list[Flowable]:
        st = self.styles.get_styles()
        elements: list[Flowable] = []

        elements.append(
            Paragraph(self.s.get("isms_title", ""), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self.s.get("isms_body", ""), st["BodyText2"])
        )

        elements.extend(self._document_categories())
        elements.extend(self._password_policy())
        elements.extend(self._rbac_profiles())
        elements.extend(self._lifecycle())

        elements.append(PageBreak())
        return elements
