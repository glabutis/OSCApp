"""Templates tab widget — list, add, edit, delete OSC command templates."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from typing import Optional

from .config import AppConfig, Template
from .osc_sender import OSCSender
from .template_dialog import TemplateDialog


class TemplateRow(QFrame):
    edit_requested = Signal(str)    # template id
    delete_requested = Signal(str)  # template id
    test_requested = Signal(str)    # template id

    def __init__(self, template: Template, parent=None) -> None:
        super().__init__(parent)
        self.template_id = template.id
        self.setObjectName("mappingRow")
        self._build(template)

    def update_template(self, template: Template) -> None:
        self._label_lbl.setText(template.label)
        self._addr_lbl.setText(template.address or "(no address)")
        self._args_lbl.setText(template.args)

    def _build(self, template: Template) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # ── Label ─────────────────────────────────────────────────────────────
        self._label_lbl = QLabel(template.label)
        self._label_lbl.setObjectName("mappingName")
        self._label_lbl.setMinimumWidth(160)
        self._label_lbl.setMaximumWidth(220)
        layout.addWidget(self._label_lbl)

        # ── OSC address (stretches) ────────────────────────────────────────────
        self._addr_lbl = QLabel(template.address or "(no address)")
        self._addr_lbl.setObjectName("mappingOsc")
        layout.addWidget(self._addr_lbl, 1)

        # ── Args ─────────────────────────────────────────────────────────────
        self._args_lbl = QLabel(template.args)
        self._args_lbl.setObjectName("templateArgs")
        self._args_lbl.setMinimumWidth(80)
        self._args_lbl.setMaximumWidth(160)
        layout.addWidget(self._args_lbl)

        # ── Test ─────────────────────────────────────────────────────────────
        test_btn = QPushButton("▶")
        test_btn.setObjectName("testButton")
        test_btn.setFixedSize(28, 28)
        test_btn.setToolTip("Send this OSC command now")
        test_btn.clicked.connect(lambda: self.test_requested.emit(self.template_id))
        layout.addWidget(test_btn)

        # ── Edit ─────────────────────────────────────────────────────────────
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("rowButton")
        edit_btn.setFixedWidth(56)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.template_id))
        layout.addWidget(edit_btn)

        # ── Delete ───────────────────────────────────────────────────────────
        del_btn = QPushButton("✕")
        del_btn.setObjectName("deleteButton")
        del_btn.setFixedSize(28, 28)
        del_btn.setToolTip("Delete template")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.template_id))
        layout.addWidget(del_btn)


class TemplatesTab(QWidget):
    """
    Second main tab — manage reusable OSC command templates.

    Emits template_updated / template_deleted so the main window can
    propagate changes to linked mappings.
    """

    template_updated = Signal(str)        # template id
    template_deleted = Signal(str, str)  # template id, template label

    def __init__(self, config: AppConfig, osc: Optional[OSCSender], parent=None) -> None:
        super().__init__(parent)
        self._config = config
        self._osc = osc
        self._rows: dict[str, TemplateRow] = {}
        self._build_ui()
        for t in config.templates:
            self._insert_row(t)

    # ── Public ───────────────────────────────────────────────────────────────

    def add_template(self, template: Template) -> None:
        """Called by main window when a template is added from mapping dialog."""
        self._config.templates.append(template)
        self._insert_row(template)

    def update_osc(self, osc: Optional[OSCSender]) -> None:
        """Update the OSCSender used for test sends."""
        self._osc = osc

    # ── Private: UI ──────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 10)
        layout.setSpacing(8)

        # Header row
        header_row = QHBoxLayout()
        section_lbl = QLabel("OSC TEMPLATES")
        section_lbl.setObjectName("sectionLabel")
        header_row.addWidget(section_lbl)
        header_row.addStretch()
        add_btn = QPushButton("+ Add Template")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self._add_template)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        hint = QLabel(
            "Save OSC commands as templates to reuse them across multiple key mappings."
        )
        hint.setObjectName("hintLabel")
        layout.addWidget(hint)

        # Column headers
        col_frame = QFrame()
        col_frame.setObjectName("colHeader")
        col_layout = QHBoxLayout(col_frame)
        col_layout.setContentsMargins(12, 2, 12, 2)
        col_layout.setSpacing(12)
        for text, min_w, stretch in [
            ("Name", 160, 0),
            ("OSC Address", 0, 1),
            ("Args", 80, 0),
            ("", 28 + 12 + 56 + 12 + 28, 0),  # spacer: ▶ + Edit + Delete
        ]:
            lbl = QLabel(text)
            lbl.setObjectName("colHeaderLabel")
            if min_w:
                lbl.setMinimumWidth(min_w)
                lbl.setMaximumWidth(min_w if not stretch else 999)
            if stretch:
                col_layout.addWidget(lbl, stretch)
            else:
                col_layout.addWidget(lbl)
        layout.addWidget(col_frame)

        # Scrollable list
        scroll = QScrollArea()
        scroll.setObjectName("mappingsScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        self._rows_container = QWidget()
        self._rows_container.setObjectName("mappingsContainer")
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(4)
        self._rows_layout.addStretch()

        # Empty state
        self._empty_lbl = QLabel("No templates yet. Click + Add Template to create one.")
        self._empty_lbl.setObjectName("emptyStateLabel")
        self._empty_lbl.setAlignment(Qt.AlignCenter)
        self._rows_layout.insertWidget(0, self._empty_lbl)

        scroll.setWidget(self._rows_container)
        layout.addWidget(scroll, 1)

    def _refresh_empty_state(self) -> None:
        self._empty_lbl.setVisible(len(self._rows) == 0)

    # ── Private: CRUD ─────────────────────────────────────────────────────────

    def _insert_row(self, template: Template) -> None:
        row = TemplateRow(template)
        row.edit_requested.connect(self._edit_template)
        row.delete_requested.connect(self._delete_template)
        row.test_requested.connect(self._test_template)
        insert_at = self._rows_layout.count() - 1
        self._rows_layout.insertWidget(insert_at, row)
        self._rows[template.id] = row
        self._refresh_empty_state()

    def _add_template(self) -> None:
        template = Template.new()
        dialog = TemplateDialog(template, self._osc or OSCSender(), self)
        if dialog.exec():
            created = dialog.get_template()
            self._config.templates.append(created)
            self._insert_row(created)
            self._config.save()

    def _edit_template(self, template_id: str) -> None:
        template = next((t for t in self._config.templates if t.id == template_id), None)
        if not template:
            return
        dialog = TemplateDialog(template.copy(), self._osc or OSCSender(), self)
        if dialog.exec():
            updated = dialog.get_template()
            for i, t in enumerate(self._config.templates):
                if t.id == template_id:
                    self._config.templates[i] = updated
                    break
            if template_id in self._rows:
                self._rows[template_id].update_template(updated)
            self._config.save()
            self.template_updated.emit(template_id)

    def _delete_template(self, template_id: str) -> None:
        from PySide6.QtWidgets import QMessageBox
        template = next((t for t in self._config.templates if t.id == template_id), None)
        if not template:
            return
        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Delete template \"{template.label}\"?\n\n"
            "Any mappings using this template will revert to custom commands.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self._config.templates = [t for t in self._config.templates if t.id != template_id]
        if template_id in self._rows:
            row = self._rows.pop(template_id)
            self._rows_layout.removeWidget(row)
            row.deleteLater()
        self._config.save()
        self._refresh_empty_state()
        self.template_deleted.emit(template_id, template.label)

    def _test_template(self, template_id: str) -> None:
        template = next((t for t in self._config.templates if t.id == template_id), None)
        if not template or not self._osc:
            return
        self._osc.send(template.address, template.args)
