"""Main application window."""

import sys
import uuid
from datetime import datetime
from typing import Callable

from PySide6.QtCore import QObject, QTimer, Qt, Signal, Slot
from PySide6.QtGui import QAction, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig, Mapping
from .input_listener import InputListener
from .mapping_dialog import MappingDialog
from .mapping_row import MappingRow
from .osc_sender import OSCSender
from .settings_dialog import SettingsDialog


class _ListenerBridge(QObject):
    """
    Bridges pynput's background thread to Qt signals.

    pynput fires callbacks from its own thread; Qt signals posted from
    non-GUI threads are safely queued to the main thread.
    """
    action_received = Signal(str, str)   # key_str, press_type
    key_captured = Signal(str)           # key_str


class MainWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self._rows: dict[str, MappingRow] = {}
        self._pending_captures: list[Callable[[str], None]] = []
        self._active = True  # master OSC enable flag

        # OSC sender
        self._osc = OSCSender(config.osc.host, config.osc.port)

        # Keyboard listener
        self._listener = InputListener()
        self._listener.set_threshold(config.settings.long_press_threshold_ms)

        # Bridge (lives in the main thread; signals are queued automatically)
        self._bridge = _ListenerBridge()
        self._bridge.action_received.connect(self._on_action)
        self._bridge.key_captured.connect(self._on_key_captured)
        self._listener.set_action_callback(self._listener_action_cb)

        self._build_ui()
        self._start_listener()
        self._setup_tray()

    # ── Keyboard capture API (called by MappingDialog via signal) ─────────────

    def request_key_capture(self, callback: Callable[[str], None]) -> None:
        self._pending_captures.append(callback)
        self._listener.capture_next_key(
            lambda ks: self._bridge.key_captured.emit(ks)
        )

    def cancel_key_capture(self) -> None:
        self._listener.cancel_capture()
        self._pending_captures.clear()

    # ── Private: listener callbacks ──────────────────────────────────────────

    def _listener_action_cb(self, key_str: str, press_type: str) -> None:
        """Called from pynput thread — emit signal to cross into main thread."""
        self._bridge.action_received.emit(key_str, press_type)

    @Slot(str, str)
    def _on_action(self, key_str: str, press_type: str) -> None:
        """Runs in main thread. Looks up matching mappings and fires OSC."""
        if not self._active:
            return
        for mapping in self.config.mappings:
            if not mapping.enabled:
                continue
            if mapping.key_str != key_str:
                continue
            if mapping.press_type not in (press_type, "any"):
                continue
            ok, err = self._osc.send(mapping.osc_address, mapping.osc_args)
            self._append_log(ok, mapping.osc_address, mapping.osc_args)
            if ok:
                self._set_status(
                    f"✓ [{mapping.name}]  {mapping.osc_address}", "success"
                )
            else:
                self._set_status(f"✗ [{mapping.name}]  {err}", "error")

    @Slot(str)
    def _on_key_captured(self, key_str: str) -> None:
        """Runs in main thread. Delivers captured key to the waiting dialog."""
        if self._pending_captures:
            cb = self._pending_captures.pop(0)
            cb(key_str)

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Dispatch")
        self.setMinimumSize(720, 520)
        self.resize(860, 620)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._make_header())
        layout.addWidget(self._make_connection_section())
        layout.addWidget(self._make_mappings_section(), 1)
        self._log_panel = self._make_log_panel()
        layout.addWidget(self._log_panel)
        layout.addWidget(self._make_status_bar())

    # ── Header ────────────────────────────────────────────────────────────────

    def _make_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)

        icon = QLabel("◎")
        icon.setObjectName("headerIcon")
        layout.addWidget(icon)

        title = QLabel("Dispatch")
        title.setObjectName("headerTitle")
        layout.addWidget(title)

        layout.addStretch()

        self._pause_btn = QPushButton("⏸  Pause")
        self._pause_btn.setObjectName("headerButton")
        self._pause_btn.setToolTip("Pause all OSC output without stopping the listener")
        self._pause_btn.clicked.connect(self._toggle_active)
        layout.addWidget(self._pause_btn)

        self._log_btn = QPushButton("Log ▾")
        self._log_btn.setObjectName("headerButton")
        self._log_btn.setToolTip("Show / hide OSC message log")
        self._log_btn.clicked.connect(self._toggle_log)
        layout.addWidget(self._log_btn)

        settings_btn = QPushButton("⚙  Settings")
        settings_btn.setObjectName("headerButton")
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)

        return frame

    # ── Connection section ────────────────────────────────────────────────────

    def _make_connection_section(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("sectionFrame")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 14, 20, 14)
        layout.setSpacing(10)

        # Row 1: section title + status
        row1 = QHBoxLayout()
        section_lbl = QLabel("OSC DESTINATION")
        section_lbl.setObjectName("sectionLabel")
        row1.addWidget(section_lbl)
        row1.addStretch()
        self._conn_dot = QLabel("●")
        self._conn_dot.setObjectName("statusDotActive")
        self._conn_status = QLabel("Ready")
        self._conn_status.setObjectName("statusText")
        row1.addWidget(self._conn_dot)
        row1.addWidget(self._conn_status)
        layout.addLayout(row1)

        # Row 2: fields
        row2 = QHBoxLayout()
        row2.setSpacing(10)

        ip_lbl = QLabel("Host")
        ip_lbl.setObjectName("fieldLabel")
        row2.addWidget(ip_lbl)

        self._host_edit = QLineEdit(self.config.osc.host)
        self._host_edit.setObjectName("inputField")
        self._host_edit.setPlaceholderText("192.168.1.100")
        self._host_edit.setMinimumWidth(160)
        self._host_edit.editingFinished.connect(self._apply_osc_config)
        row2.addWidget(self._host_edit)

        port_lbl = QLabel("Port")
        port_lbl.setObjectName("fieldLabel")
        row2.addWidget(port_lbl)

        self._port_edit = QLineEdit(str(self.config.osc.port))
        self._port_edit.setObjectName("inputField")
        self._port_edit.setPlaceholderText("3333")
        self._port_edit.setMaximumWidth(75)
        self._port_edit.setValidator(QIntValidator(1, 65535))
        self._port_edit.editingFinished.connect(self._apply_osc_config)
        row2.addWidget(self._port_edit)

        test_btn = QPushButton("Test")
        test_btn.setObjectName("rowButton")
        test_btn.setToolTip("Send a test OSC message to verify connectivity")
        test_btn.clicked.connect(self._send_test_osc)
        row2.addWidget(test_btn)

        row2.addStretch()
        layout.addLayout(row2)

        return frame

    # ── Mappings section ──────────────────────────────────────────────────────

    def _make_mappings_section(self) -> QWidget:
        outer = QWidget()
        outer.setObjectName("mappingsSectionOuter")
        layout = QVBoxLayout(outer)
        layout.setContentsMargins(20, 14, 20, 10)
        layout.setSpacing(8)

        # Header row
        header_row = QHBoxLayout()
        section_lbl = QLabel("KEY MAPPINGS")
        section_lbl.setObjectName("sectionLabel")
        header_row.addWidget(section_lbl)
        header_row.addStretch()
        add_btn = QPushButton("+ Add Mapping")
        add_btn.setObjectName("addButton")
        add_btn.clicked.connect(self._add_mapping)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Column headers
        col_frame = QFrame()
        col_frame.setObjectName("colHeader")
        col_layout = QHBoxLayout(col_frame)
        col_layout.setContentsMargins(46, 2, 12, 2)
        col_layout.setSpacing(12)
        for text, min_w, stretch in [
            ("Name", 130, 0),
            ("Key", 90, 0),
            ("Type", 52, 0),
            ("OSC Address", 0, 1),
            ("", 28 + 12 + 56 + 12 + 56 + 28, 0),  # spacer: ▶ + Copy + Edit + Delete
        ]:
            lbl = QLabel(text)
            lbl.setObjectName("colHeaderLabel")
            if min_w:
                lbl.setMinimumWidth(min_w)
                lbl.setMaximumWidth(min_w)
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

        scroll.setWidget(self._rows_container)
        layout.addWidget(scroll, 1)

        # Populate with saved mappings
        for m in self.config.mappings:
            self._insert_row(m)

        return outer

    # ── OSC Log panel ─────────────────────────────────────────────────────────

    def _make_log_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("logPanelFrame")
        frame.setFixedHeight(150)
        frame.setVisible(False)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(0)

        self._log_edit = QPlainTextEdit()
        self._log_edit.setObjectName("oscLogEdit")
        self._log_edit.setReadOnly(True)
        self._log_edit.setMaximumBlockCount(200)
        self._log_edit.setPlaceholderText("OSC messages will appear here…")
        layout.addWidget(self._log_edit)

        return frame

    # ── Status bar ────────────────────────────────────────────────────────────

    def _make_status_bar(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("statusBarFrame")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(8)

        self._listener_dot = QLabel("●")
        self._listener_dot.setObjectName("listenerDotActive")
        layout.addWidget(self._listener_dot)

        self._listener_lbl = QLabel("Listening for input")
        self._listener_lbl.setObjectName("listenerStatus")
        layout.addWidget(self._listener_lbl)

        layout.addStretch()

        self._last_action_lbl = QLabel("")
        self._last_action_lbl.setObjectName("lastAction")
        layout.addWidget(self._last_action_lbl)

        return frame

    # ── Mapping CRUD ──────────────────────────────────────────────────────────

    def _insert_row(self, mapping: Mapping) -> None:
        row = MappingRow(mapping)
        row.edit_requested.connect(self._edit_mapping)
        row.delete_requested.connect(self._delete_mapping)
        row.toggle_requested.connect(self._toggle_mapping)
        row.duplicate_requested.connect(self._duplicate_mapping)
        row.test_requested.connect(self._test_mapping)
        insert_at = self._rows_layout.count() - 1
        self._rows_layout.insertWidget(insert_at, row)
        self._rows[mapping.id] = row

    def _add_mapping(self) -> None:
        mapping = Mapping.new()
        dialog = MappingDialog(mapping, self)
        dialog.key_capture_requested.connect(self.request_key_capture)
        dialog.key_capture_cancelled.connect(self.cancel_key_capture)
        if dialog.exec():
            updated = dialog.get_mapping()
            self.config.mappings.append(updated)
            self._insert_row(updated)
            self.config.save()

    def _edit_mapping(self, mapping_id: str) -> None:
        mapping = next((m for m in self.config.mappings if m.id == mapping_id), None)
        if not mapping:
            return
        dialog = MappingDialog(mapping.copy(), self)
        dialog.key_capture_requested.connect(self.request_key_capture)
        dialog.key_capture_cancelled.connect(self.cancel_key_capture)
        if dialog.exec():
            updated = dialog.get_mapping()
            for i, m in enumerate(self.config.mappings):
                if m.id == mapping_id:
                    self.config.mappings[i] = updated
                    break
            if mapping_id in self._rows:
                self._rows[mapping_id].update_mapping(updated)
            self.config.save()

    def _delete_mapping(self, mapping_id: str) -> None:
        reply = QMessageBox.question(
            self,
            "Delete Mapping",
            "Delete this mapping?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return
        self.config.mappings = [m for m in self.config.mappings if m.id != mapping_id]
        if mapping_id in self._rows:
            row = self._rows.pop(mapping_id)
            self._rows_layout.removeWidget(row)
            row.deleteLater()
        self.config.save()

    def _toggle_mapping(self, mapping_id: str, enabled: bool) -> None:
        for m in self.config.mappings:
            if m.id == mapping_id:
                m.enabled = enabled
                break
        self.config.save()

    def _duplicate_mapping(self, mapping_id: str) -> None:
        mapping = next((m for m in self.config.mappings if m.id == mapping_id), None)
        if not mapping:
            return
        dup = mapping.copy()
        dup.id = str(uuid.uuid4())
        dup.name = f"Copy of {mapping.name}"

        # Insert after the original in the config list
        orig_idx = next(i for i, m in enumerate(self.config.mappings) if m.id == mapping_id)
        self.config.mappings.insert(orig_idx + 1, dup)

        # Build row and insert after the original row widget
        row = MappingRow(dup)
        row.edit_requested.connect(self._edit_mapping)
        row.delete_requested.connect(self._delete_mapping)
        row.toggle_requested.connect(self._toggle_mapping)
        row.duplicate_requested.connect(self._duplicate_mapping)
        row.test_requested.connect(self._test_mapping)
        orig_row = self._rows.get(mapping_id)
        if orig_row:
            insert_at = self._rows_layout.indexOf(orig_row) + 1
        else:
            insert_at = self._rows_layout.count() - 1
        self._rows_layout.insertWidget(insert_at, row)
        self._rows[dup.id] = row
        self.config.save()

    def _test_mapping(self, mapping_id: str) -> None:
        mapping = next((m for m in self.config.mappings if m.id == mapping_id), None)
        if not mapping:
            return
        ok, err = self._osc.send(mapping.osc_address, mapping.osc_args)
        self._append_log(ok, mapping.osc_address, mapping.osc_args)
        if ok:
            self._set_status(f"✓ Test [{mapping.name}]  {mapping.osc_address}", "success")
        else:
            self._set_status(f"✗ Test failed [{mapping.name}]  {err}", "error")

    # ── Master toggle ─────────────────────────────────────────────────────────

    def _toggle_active(self) -> None:
        self._active = not self._active
        if self._active:
            self._pause_btn.setText("⏸  Pause")
            self._pause_btn.setObjectName("headerButton")
        else:
            self._pause_btn.setText("▶  Resume")
            self._pause_btn.setObjectName("pausedButton")
        self._pause_btn.style().unpolish(self._pause_btn)
        self._pause_btn.style().polish(self._pause_btn)

    # ── OSC Log ───────────────────────────────────────────────────────────────

    def _toggle_log(self) -> None:
        visible = not self._log_panel.isVisible()
        self._log_panel.setVisible(visible)
        self._log_btn.setText("Log ▴" if visible else "Log ▾")

    def _append_log(self, ok: bool, address: str, args_str: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        symbol = "✓" if ok else "✗"
        line = f"{ts}  {symbol}  {address}"
        if args_str.strip():
            line += f"  {args_str.strip()}"
        self._log_edit.appendPlainText(line)

    # ── System tray ───────────────────────────────────────────────────────────

    def _setup_tray(self) -> None:
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(QApplication.instance().windowIcon())
        self._tray.setToolTip("Dispatch")

        menu = QMenu(self)
        show_action = QAction("Show / Hide", self)
        show_action.triggered.connect(self._toggle_visibility)
        menu.addAction(show_action)
        menu.addSeparator()
        quit_action = QAction("Quit Dispatch", self)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._toggle_visibility()

    def _quit_app(self) -> None:
        self._tray.hide()
        self._listener.stop()
        self.config.save()
        QApplication.quit()

    # ── OSC config ────────────────────────────────────────────────────────────

    def _apply_osc_config(self) -> None:
        host = self._host_edit.text().strip()
        try:
            port = int(self._port_edit.text())
        except ValueError:
            port = 3333
        if host:
            self.config.osc.host = host
            self.config.osc.port = port
            self._osc.update(host, port)
            self.config.save()

    def _send_test_osc(self) -> None:
        self._apply_osc_config()
        ok, err = self._osc.send("/dispatch/test", "1")
        self._append_log(ok, "/dispatch/test", "1")
        if ok:
            self._set_status("✓ Test message sent", "success")
        else:
            self._set_status(f"✗ Send failed: {err}", "error")

    # ── Settings ──────────────────────────────────────────────────────────────

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.config.settings, self)
        if dialog.exec():
            updated = dialog.get_settings()
            self.config.settings = updated
            self._listener.set_threshold(updated.long_press_threshold_ms)
            self.config.save()

    # ── Listener start ────────────────────────────────────────────────────────

    def _start_listener(self) -> None:
        try:
            self._listener.start()
        except Exception as exc:
            self._listener_dot.setObjectName("listenerDotInactive")
            self._listener_lbl.setText(f"Listener error: {exc}")
            if sys.platform == "darwin":
                QMessageBox.warning(
                    self,
                    "Accessibility Permission Required",
                    "Dispatch needs Accessibility access to capture global key events.\n\n"
                    "Open System Settings → Privacy & Security → Accessibility\n"
                    "and enable Dispatch.",
                )

    # ── Status helper ─────────────────────────────────────────────────────────

    def _set_status(self, message: str, level: str = "normal") -> None:
        colors = {
            "success": "#a6e3a1",
            "error": "#f38ba8",
            "normal": "#a6adc8",
        }
        color = colors.get(level, colors["normal"])
        self._last_action_lbl.setText(message)
        self._last_action_lbl.setStyleSheet(f"color: {color};")
        QTimer.singleShot(4000, lambda: self._last_action_lbl.setText(""))

    # ── Window lifecycle ──────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        if QSystemTrayIcon.isSystemTrayAvailable() and self._tray.isVisible():
            self.hide()
            event.ignore()
            return
        self._listener.stop()
        self.config.save()
        super().closeEvent(event)
