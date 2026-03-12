"""A single row widget in the mappings list."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton

from .config import Mapping
from .key_utils import key_display


class MappingRow(QFrame):
    edit_requested = Signal(str)    # mapping id
    delete_requested = Signal(str)  # mapping id
    toggle_requested = Signal(str, bool)  # mapping id, enabled

    def __init__(self, mapping: Mapping, parent=None) -> None:
        super().__init__(parent)
        self.mapping_id = mapping.id
        self.setObjectName("mappingRow")
        self._build(mapping)

    # ── Public ───────────────────────────────────────────────────────────────

    def update_mapping(self, mapping: Mapping) -> None:
        self._name_lbl.setText(mapping.name)
        self._key_lbl.setText(key_display(mapping.key_str))
        self._set_badge(mapping.press_type)
        self._osc_lbl.setText(mapping.osc_address or "(no address)")
        self._dot_btn.setChecked(mapping.enabled)
        self._refresh_dot(mapping.enabled)

    # ── Private ───────────────────────────────────────────────────────────────

    def _build(self, mapping: Mapping) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # ── Enabled toggle dot ──────────────────────────────────────────────
        self._dot_btn = QPushButton("●")
        self._dot_btn.setObjectName("enabledDot")
        self._dot_btn.setFixedSize(22, 22)
        self._dot_btn.setCheckable(True)
        self._dot_btn.setChecked(mapping.enabled)
        self._dot_btn.setToolTip("Toggle enabled / disabled")
        self._dot_btn.clicked.connect(
            lambda checked: self.toggle_requested.emit(self.mapping_id, checked)
        )
        self._refresh_dot(mapping.enabled)
        layout.addWidget(self._dot_btn)

        # ── Name ─────────────────────────────────────────────────────────────
        self._name_lbl = QLabel(mapping.name)
        self._name_lbl.setObjectName("mappingName")
        self._name_lbl.setMinimumWidth(130)
        self._name_lbl.setMaximumWidth(200)
        layout.addWidget(self._name_lbl)

        # ── Key ──────────────────────────────────────────────────────────────
        self._key_lbl = QLabel(key_display(mapping.key_str))
        self._key_lbl.setObjectName("mappingKey")
        self._key_lbl.setMinimumWidth(90)
        self._key_lbl.setMaximumWidth(130)
        layout.addWidget(self._key_lbl)

        # ── Press-type badge ─────────────────────────────────────────────────
        self._badge_lbl = QLabel()
        self._badge_lbl.setFixedWidth(52)
        self._badge_lbl.setAlignment(Qt.AlignCenter)
        self._set_badge(mapping.press_type)
        layout.addWidget(self._badge_lbl)

        # ── OSC address (stretches to fill) ──────────────────────────────────
        self._osc_lbl = QLabel(mapping.osc_address or "(no address)")
        self._osc_lbl.setObjectName("mappingOsc")
        layout.addWidget(self._osc_lbl, 1)

        # ── Edit ─────────────────────────────────────────────────────────────
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("rowButton")
        edit_btn.setFixedWidth(56)
        edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.mapping_id))
        layout.addWidget(edit_btn)

        # ── Delete ───────────────────────────────────────────────────────────
        del_btn = QPushButton("✕")
        del_btn.setObjectName("deleteButton")
        del_btn.setFixedSize(28, 28)
        del_btn.setToolTip("Delete mapping")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self.mapping_id))
        layout.addWidget(del_btn)

    def _set_badge(self, press_type: str) -> None:
        name_map = {"short": "SHORT", "long": "LONG", "any": "ANY"}
        obj_map = {"short": "badgeShort", "long": "badgeLong", "any": "badgeAny"}
        self._badge_lbl.setText(name_map.get(press_type, press_type.upper()))
        self._badge_lbl.setObjectName(obj_map.get(press_type, "badgeAny"))
        # Force Qt to re-apply the style
        self._badge_lbl.style().unpolish(self._badge_lbl)
        self._badge_lbl.style().polish(self._badge_lbl)

    def _refresh_dot(self, enabled: bool) -> None:
        self._dot_btn.setProperty("enabled_state", "on" if enabled else "off")
        self._dot_btn.style().unpolish(self._dot_btn)
        self._dot_btn.style().polish(self._dot_btn)
