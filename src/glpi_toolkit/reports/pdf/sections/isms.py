"""ISMS integration section — documents, password policy, RBAC, lifecycle."""

from __future__ import annotations

from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, PageBreak, Paragraph, Spacer

from glpi_toolkit.reports.pdf.components import make_table
from glpi_toolkit.reports.pdf.sections.base import BaseSection

PAGE_WIDTH, _ = A4
USABLE = PAGE_WIDTH - 60


class ISMSSection(BaseSection):
    """Renders the ISMS integration section."""

    def _document_categories(self) -> list[Flowable]:
        st = self.styles.get_styles()
        doc_cats = self.config.assets.document_categories
        isms_docs = [c for c in doc_cats if "ISMS" in c or "Audit" in c or "Procedure" in c]
        other_docs = [c for c in doc_cats if c not in isms_docs]

        elements: list[Flowable] = [
            Paragraph(self._s("isms_docs_title"), st["SubSection"]),
            Paragraph(self._s("isms_docs_body"), st["BodyText2"]),
        ]
        for doc in isms_docs:
            elements.append(Paragraph(f"\u2022 {doc}", st["BulletItem"]))
        if other_docs:
            elements.append(Spacer(1, 4))
            elements.append(
                Paragraph(self._s("isms_docs_other"), st["BodyText2"])
            )
            for doc in other_docs:
                elements.append(Paragraph(f"\u2022 {doc}", st["BulletItem"]))
        elements.append(Spacer(1, 12))
        return elements

    def _password_policy(self) -> list[Flowable]:
        st = self.styles.get_styles()
        pwd = self.config.security.password_policy
        lockout = self.config.security.account_lockout

        header = [self._s("isms_pwd_setting"), self._s("isms_pwd_value")]
        rows: list[list[str]] = [header]
        field_map = [
            ("isms_pwd_min_length", str(pwd.min_length)),
            ("isms_pwd_uppercase", self._yesno(pwd.require_uppercase)),
            ("isms_pwd_lowercase", self._yesno(pwd.require_lowercase)),
            ("isms_pwd_number", self._yesno(pwd.require_number)),
            ("isms_pwd_symbol", self._yesno(pwd.require_symbol)),
            ("isms_pwd_expiry", f"{pwd.expiry_days} {self._s('days')}"),
            ("isms_pwd_max_attempts", str(lockout.max_attempts)),
            ("isms_pwd_lockout", f"{lockout.lockout_minutes} {self._s('minutes')}"),
        ]
        for key, val in field_map:
            rows.append([self._s(key, key), val])

        return [
            Paragraph(self._s("isms_pwd_title"), st["SubSection"]),
            Paragraph(self._s("isms_pwd_body"), st["BodyText2"]),
            Paragraph(self._s("isms_pwd_ref"), st["ISORef"]),
            make_table(rows, [USABLE * 0.55, USABLE * 0.45], report_colors=self.styles.colors),
            Spacer(1, 12),
        ]

    def _rbac_profiles(self) -> list[Flowable]:
        st = self.styles.get_styles()
        profiles = self.config.security.profiles
        header = [
            self._s("isms_rbac_role"),
            self._s("isms_rbac_desc"),
            self._s("isms_rbac_tickets"),
            self._s("isms_rbac_admin"),
        ]
        rows: list[list[str]] = [header]
        for p in profiles:
            rows.append([
                p.name,
                p.description,
                p.permissions.tickets,
                self._yesno(p.permissions.admin),
            ])

        return [
            Paragraph(self._s("isms_rbac_title"), st["SubSection"]),
            Paragraph(self._s("isms_rbac_body"), st["BodyText2"]),
            make_table(
                rows,
                [USABLE * 0.15, USABLE * 0.40, USABLE * 0.20, USABLE * 0.25],
                report_colors=self.styles.colors,
            ),
            Spacer(1, 12),
        ]

    def _lifecycle(self) -> list[Flowable]:
        st = self.styles.get_styles()
        templates = self.config.templates
        lifecycle_tpls = [t for t in templates if t.isms_ref == "ISMS-PRO-002"]

        elements: list[Flowable] = [
            Paragraph(self._s("isms_lifecycle_title"), st["SubSection"]),
            Paragraph(self._s("isms_lifecycle_body"), st["BodyText2"]),
        ]
        for tpl in lifecycle_tpls:
            elements.append(Paragraph(f"<b>{tpl.name}</b>", st["BodyText2"]))
            for item in tpl.checklist:
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
            Paragraph(self._s("isms_title"), st["SectionTitle"])
        )
        elements.append(Spacer(1, 6))
        elements.append(
            Paragraph(self._s("isms_body"), st["BodyText2"])
        )

        elements.extend(self._document_categories())
        elements.extend(self._password_policy())
        elements.extend(self._rbac_profiles())
        elements.extend(self._lifecycle())

        elements.append(PageBreak())
        return elements
