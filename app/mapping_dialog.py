"""Dialog for creating or editing a single key → OSC mapping."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .config import Mapping
from .key_utils import key_display


class MappingDialog(QDialog):
    """
    Modal dialog to create or edit a Mapping.

    Key-capture is delegated back to the main window so the global listener
    can intercept the next keystroke.  The dialog emits signals to request
    capture and to cancel it.
    """

    key_capture_requested = Signal(object)   # delivers a Python callable
    key_capture_cancelled = Signal()

    def __init__(self, mapping: Mapping, parent=None) -> None:
        super().__init__(parent)
        self._mapping = mapping
        self._listening = False

        self.setWindowTitle("Edit Mapping" if mapping.key_str else "New Mapping")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        self._build_ui()
        self._populate(mapping)

    # ── Public ───────────────────────────────────────────────────────────────

    def get_mapping(self) -> Mapping:
        """Return the mapping with current dialog values applied."""
        m = self._mapping.copy()
        m.name = self._name_edit.text().strip() or "Unnamed"
        m.press_type = self._get_press_type()
        m.osc_address = self._osc_addr_edit.text().strip()
        m.osc_args = self._osc_args_edit.text().strip()
        m.enabled = self._enabled_cb.isChecked()
        return m

    # ── Signal handlers (called by main window via signal) ────────────────────

    def on_key_captured(self, key_str: str) -> None:
        """Called when the global listener has captured a key."""
        self._mapping.key_str = key_str
        self._update_key_display(key_str)
        self._set_listening(False)

    # ── Private ───────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(20)

        # ── Name ─────────────────────────────────────────────────────────────
        root.addWidget(self._section_label("NAME"))
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g. Forward Long Press")
        root.addWidget(self._name_edit)

        # ── Key binding ──────────────────────────────────────────────────────
        root.addWidget(self._section_label("KEY BINDING"))

        key_row = QHBoxLayout()
        key_row.setSpacing(10)

        key_panel = QFrame()
        key_panel.setObjectName("keyDisplayPanel")
        key_panel_layout = QHBoxLayout(key_panel)
        key_panel_layout.setContentsMargins(12, 8, 12, 8)
        self._key_display_lbl = QLabel("Not set")
        self._key_display_lbl.setObjectName("keyDisplayLabel")
        self._capture_status_lbl = QLabel("")
        self._capture_status_lbl.setObjectName("captureLabel")
        key_panel_layout.addWidget(self._key_display_lbl)
        key_panel_layout.addStretch()
        key_panel_layout.addWidget(self._capture_status_lbl)

        key_row.addWidget(key_panel, 1)

        self._listen_btn = QPushButton("Listen")
        self._listen_btn.setObjectName("listenButton")
        self._listen_btn.setFixedWidth(80)
        self._listen_btn.setToolTip(
            "Click then press a key on your remote to capture it"
        )
        self._listen_btn.clicked.connect(self._toggle_listen)
        key_row.addWidget(self._listen_btn)

        root.addLayout(key_row)

        hint = QLabel(
            "Click Listen, then press any key on your remote. "
            "Hold for long press detection."
        )
        hint.setObjectName("hintLabel")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # ── Press type ───────────────────────────────────────────────────────
        root.addWidget(self._section_label("PRESS TYPE"))

        radio_row = QHBoxLayout()
        radio_row.setSpacing(20)

        self._radio_short = QRadioButton("Short press")
        self._radio_long = QRadioButton("Long press")
        self._radio_any = QRadioButton("Any (both)")

        self._press_type_group = QButtonGroup(self)
        self._press_type_group.addButton(self._radio_short)
        self._press_type_group.addButton(self._radio_long)
        self._press_type_group.addButton(self._radio_any)

        radio_row.addWidget(self._radio_short)
        radio_row.addWidget(self._radio_long)
        radio_row.addWidget(self._radio_any)
        radio_row.addStretch()
        root.addLayout(radio_row)

        # ── OSC address ──────────────────────────────────────────────────────
        root.addWidget(self._section_label("OSC ADDRESS"))
        self._osc_addr_edit = QLineEdit()
        self._osc_addr_edit.setPlaceholderText("/atem/cut")
        root.addWidget(self._osc_addr_edit)

        # ── OSC arguments ─────────────────────────────────────────────────────
        root.addWidget(self._section_label("OSC ARGUMENTS  (optional)"))
        self._osc_args_edit = QLineEdit()
        self._osc_args_edit.setPlaceholderText('e.g.  1   or   2.5   or   "text"')
        root.addWidget(self._osc_args_edit)

        args_hint = QLabel(
            "Space-separated values. Integers and floats are detected automatically."
        )
        args_hint.setObjectName("hintLabel")
        root.addWidget(args_hint)

        # ── Enabled toggle ────────────────────────────────────────────────────
        divider = QFrame()
        divider.setObjectName("divider")
        root.addWidget(divider)

        self._enabled_cb = QCheckBox("Mapping enabled")
        root.addWidget(self._enabled_cb)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        root.addLayout(btn_row)

    def _populate(self, mapping: Mapping) -> None:
        self._name_edit.setText(mapping.name)
        self._update_key_display(mapping.key_str)
        {
            "short": self._radio_short,
            "long": self._radio_long,
            "any": self._radio_any,
        }.get(mapping.press_type, self._radio_short).setChecked(True)
        self._osc_addr_edit.setText(mapping.osc_address)
        self._osc_args_edit.setText(mapping.osc_args)
        self._enabled_cb.setChecked(mapping.enabled)

    def _get_press_type(self) -> str:
        if self._radio_long.isChecked():
            return "long"
        if self._radio_any.isChecked():
            return "any"
        return "short"

    def _toggle_listen(self) -> None:
        if self._listening:
            self._set_listening(False)
            self.key_capture_cancelled.emit()
        else:
            self._set_listening(True)
            self.key_capture_requested.emit(self.on_key_captured)

    def _set_listening(self, active: bool) -> None:
        self._listening = active
        if active:
            self._listen_btn.setText("Cancel")
            self._listen_btn.setObjectName("listeningActiveButton")
            self._capture_status_lbl.setText("⬤ Waiting for key…")
        else:
            self._listen_btn.setText("Listen")
            self._listen_btn.setObjectName("listenButton")
            self._capture_status_lbl.setText("")
        # Force stylesheet re-evaluation
        self._listen_btn.style().unpolish(self._listen_btn)
        self._listen_btn.style().polish(self._listen_btn)

    def _update_key_display(self, key_str: str) -> None:
        self._key_display_lbl.setText(key_display(key_str))

    def _save(self) -> None:
        if self._listening:
            self._set_listening(False)
            self.key_capture_cancelled.emit()
        self.accept()

    def reject(self) -> None:
        if self._listening:
            self._set_listening(False)
            self.key_capture_cancelled.emit()
        super().reject()

    @staticmethod
    def _section_label(text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("dialogSectionLabel")
        return lbl
