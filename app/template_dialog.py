"""Dialog for creating or editing an OSC command template."""

from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)

from .config import Template
from .osc_sender import OSCSender


class TemplateDialog(QDialog):
    """Modal dialog to create or edit a Template."""

    def __init__(self, template: Template, osc: OSCSender, parent=None) -> None:
        super().__init__(parent)
        self._template = template
        self._osc = osc

        self.setWindowTitle("Edit Template" if template.label else "New Template")
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self._build_ui()
        self._populate(template)

    # ── Public ───────────────────────────────────────────────────────────────

    def get_template(self) -> Template:
        t = self._template.copy()
        t.label = self._label_edit.text().strip()
        t.address = self._addr_edit.text().strip()
        t.args = self._args_edit.text().strip()
        return t

    # ── Private ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(20)

        # ── Label ─────────────────────────────────────────────────────────────
        root.addWidget(self._section_label("TEMPLATE NAME"))
        self._label_edit = QLineEdit()
        self._label_edit.setPlaceholderText("e.g. Fade to Black")
        root.addWidget(self._label_edit)

        # ── OSC address ───────────────────────────────────────────────────────
        root.addWidget(self._section_label("OSC ADDRESS"))
        self._addr_edit = QLineEdit()
        self._addr_edit.setPlaceholderText("/atem/cut")
        root.addWidget(self._addr_edit)

        # ── OSC arguments ─────────────────────────────────────────────────────
        root.addWidget(self._section_label("OSC ARGUMENTS  (optional)"))
        self._args_edit = QLineEdit()
        self._args_edit.setPlaceholderText('e.g.  1   or   2.5   or   "text"')
        root.addWidget(self._args_edit)

        args_hint = QLabel(
            "Space-separated values. Integers and floats are detected automatically."
        )
        args_hint.setObjectName("hintLabel")
        root.addWidget(args_hint)

        # ── Validation error ──────────────────────────────────────────────────
        self._error_lbl = QLabel("")
        self._error_lbl.setObjectName("errorLabel")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setVisible(False)
        root.addWidget(self._error_lbl)

        # ── Divider ───────────────────────────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("divider")
        root.addWidget(divider)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()

        test_btn = QPushButton("▶  Test")
        test_btn.setObjectName("testOutlineButton")
        test_btn.setToolTip("Send this OSC command now to test it")
        test_btn.clicked.connect(self._test)
        btn_row.addWidget(test_btn)

        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save Template")
        save_btn.setObjectName("primaryButton")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        root.addLayout(btn_row)

    def _populate(self, template: Template) -> None:
        self._label_edit.setText(template.label)
        self._addr_edit.setText(template.address)
        self._args_edit.setText(template.args)

    def _test(self) -> None:
        addr = self._addr_edit.text().strip()
        args = self._args_edit.text().strip()
        if not addr or not addr.startswith("/"):
            self._show_error("Enter a valid OSC address starting with / to test.")
            return
        self._osc.send(addr, args)

    def _save(self) -> None:
        errors = []
        if not self._label_edit.text().strip():
            errors.append("A template name is required.")
        addr = self._addr_edit.text().strip()
        if not addr:
            errors.append("An OSC address is required.")
        elif not addr.startswith("/"):
            errors.append('OSC address must start with "/".')

        if errors:
            self._show_error("  •  " + "\n  •  ".join(errors))
            return

        self._error_lbl.setVisible(False)
        self.accept()

    def _show_error(self, msg: str) -> None:
        self._error_lbl.setText(msg)
        self._error_lbl.setVisible(True)

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("dialogSectionLabel")
        return lbl
