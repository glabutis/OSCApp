# Catppuccin Mocha-inspired dark theme

COLORS = {
    "base": "#1e1e2e",
    "mantle": "#181825",
    "crust": "#11111b",
    "surface0": "#313244",
    "surface1": "#45475a",
    "surface2": "#585b70",
    "overlay0": "#6c7086",
    "overlay1": "#7f849c",
    "text": "#cdd6f4",
    "subtext0": "#a6adc8",
    "subtext1": "#bac2de",
    "lavender": "#b4befe",
    "blue": "#89b4fa",
    "sapphire": "#74c7ec",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "peach": "#fab387",
    "red": "#f38ba8",
    "mauve": "#cba6f7",
    "teal": "#94e2d5",
}

STYLESHEET = f"""
/* ─── Base ─────────────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {COLORS["base"]};
    color: {COLORS["text"]};
}}

QWidget {{
    background-color: transparent;
    color: {COLORS["text"]};
    font-family: "SF Pro Display", "Inter", "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    selection-background-color: {COLORS["lavender"]};
    selection-color: {COLORS["base"]};
}}

/* ─── Scrollbars ────────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {COLORS["surface1"]};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {COLORS["surface2"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: none;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}

/* ─── QFrame sections ───────────────────────────── */
#headerFrame {{
    background-color: {COLORS["mantle"]};
    border-bottom: 1px solid {COLORS["surface0"]};
}}

#sectionFrame {{
    background-color: {COLORS["mantle"]};
    border-bottom: 1px solid {COLORS["surface0"]};
}}

#mappingsSectionOuter {{
    background-color: {COLORS["base"]};
}}

#statusBarFrame {{
    background-color: {COLORS["mantle"]};
    border-top: 1px solid {COLORS["surface0"]};
}}

#colHeader {{
    background-color: transparent;
}}

#mappingsContainer {{
    background-color: transparent;
}}

/* ─── Mapping rows ──────────────────────────────── */
#mappingRow {{
    background-color: {COLORS["surface0"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 8px;
}}
#mappingRow:hover {{
    background-color: {COLORS["surface1"]};
    border: 1px solid {COLORS["surface2"]};
}}

/* ─── Labels ────────────────────────────────────── */
#headerIcon {{
    color: {COLORS["lavender"]};
    font-size: 22px;
}}
#headerTitle {{
    color: {COLORS["text"]};
    font-size: 17px;
    font-weight: 600;
}}
#sectionLabel {{
    color: {COLORS["overlay1"]};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}
#colHeaderLabel {{
    color: {COLORS["overlay0"]};
    font-size: 11px;
    font-weight: 600;
}}
#mappingName {{
    color: {COLORS["text"]};
    font-weight: 500;
}}
#mappingKey {{
    color: {COLORS["subtext0"]};
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
}}
#mappingOsc {{
    color: {COLORS["blue"]};
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 12px;
}}
#fieldLabel {{
    color: {COLORS["subtext0"]};
    font-size: 12px;
}}
#statusText {{
    color: {COLORS["subtext0"]};
    font-size: 12px;
}}
#listenerStatus {{
    color: {COLORS["subtext0"]};
    font-size: 12px;
}}
#lastAction {{
    color: {COLORS["subtext0"]};
    font-size: 12px;
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Consolas", monospace;
}}
#dialogSectionLabel {{
    color: {COLORS["overlay1"]};
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}}
#hintLabel {{
    color: {COLORS["overlay0"]};
    font-size: 11px;
}}
#captureLabel {{
    color: {COLORS["yellow"]};
    font-size: 12px;
    font-style: italic;
}}
#keyDisplayLabel {{
    color: {COLORS["teal"]};
    font-family: "SF Mono", "JetBrains Mono", "Fira Code", "Consolas", monospace;
    font-size: 13px;
    font-weight: 600;
}}
#warningLabel {{
    color: {COLORS["yellow"]};
    font-size: 12px;
}}
#errorLabel {{
    color: {COLORS["red"]};
    font-size: 12px;
}}

/* ─── Status dots ───────────────────────────────── */
#statusDotActive {{
    color: {COLORS["green"]};
    font-size: 10px;
}}
#statusDotInactive {{
    color: {COLORS["surface2"]};
    font-size: 10px;
}}
#listenerDotActive {{
    color: {COLORS["green"]};
    font-size: 10px;
}}
#listenerDotInactive {{
    color: {COLORS["red"]};
    font-size: 10px;
}}

/* ─── Type badges ───────────────────────────────── */
#badgeShort {{
    background-color: rgba(137, 180, 250, 0.15);
    color: {COLORS["blue"]};
    border: 1px solid rgba(137, 180, 250, 0.3);
    border-radius: 4px;
    padding: 1px 4px;
    font-size: 10px;
    font-weight: 700;
}}
#badgeLong {{
    background-color: rgba(203, 166, 247, 0.15);
    color: {COLORS["mauve"]};
    border: 1px solid rgba(203, 166, 247, 0.3);
    border-radius: 4px;
    padding: 1px 4px;
    font-size: 10px;
    font-weight: 700;
}}
#badgeAny {{
    background-color: rgba(148, 226, 213, 0.15);
    color: {COLORS["teal"]};
    border: 1px solid rgba(148, 226, 213, 0.3);
    border-radius: 4px;
    padding: 1px 4px;
    font-size: 10px;
    font-weight: 700;
}}

/* ─── Enabled dot button ────────────────────────── */
#enabledDot {{
    background: transparent;
    border: none;
    font-size: 14px;
    padding: 0;
}}
#enabledDot[enabled_state="on"] {{
    color: {COLORS["green"]};
}}
#enabledDot[enabled_state="off"] {{
    color: {COLORS["surface2"]};
}}

/* ─── Buttons ───────────────────────────────────── */
QPushButton {{
    background-color: {COLORS["surface0"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
}}
QPushButton:hover {{
    background-color: {COLORS["surface1"]};
    border-color: {COLORS["surface2"]};
}}
QPushButton:pressed {{
    background-color: {COLORS["surface2"]};
}}
QPushButton:disabled {{
    color: {COLORS["overlay0"]};
    background-color: {COLORS["surface0"]};
    border-color: {COLORS["surface0"]};
}}

#headerButton {{
    background-color: transparent;
    color: {COLORS["subtext0"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
}}
#headerButton:hover {{
    background-color: {COLORS["surface0"]};
    color: {COLORS["text"]};
}}

#addButton {{
    background-color: rgba(180, 190, 254, 0.15);
    color: {COLORS["lavender"]};
    border: 1px solid rgba(180, 190, 254, 0.3);
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 600;
}}
#addButton:hover {{
    background-color: rgba(180, 190, 254, 0.25);
    border-color: {COLORS["lavender"]};
}}

#rowButton {{
    background-color: transparent;
    color: {COLORS["subtext0"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 5px;
    padding: 3px 8px;
    font-size: 12px;
}}
#rowButton:hover {{
    background-color: {COLORS["surface1"]};
    color: {COLORS["text"]};
}}

#deleteButton {{
    background-color: transparent;
    color: {COLORS["surface2"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 5px;
    padding: 2px;
    font-size: 12px;
    font-weight: 700;
}}
#deleteButton:hover {{
    background-color: rgba(243, 139, 168, 0.15);
    color: {COLORS["red"]};
    border-color: rgba(243, 139, 168, 0.4);
}}

#primaryButton {{
    background-color: {COLORS["lavender"]};
    color: {COLORS["base"]};
    border: none;
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 13px;
    font-weight: 600;
}}
#primaryButton:hover {{
    background-color: #c6d0fe;
}}
#primaryButton:pressed {{
    background-color: #a0aeee;
}}

#cancelButton {{
    background-color: transparent;
    color: {COLORS["subtext0"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
    padding: 7px 20px;
    font-size: 13px;
}}
#cancelButton:hover {{
    background-color: {COLORS["surface0"]};
    color: {COLORS["text"]};
}}

#listenButton {{
    background-color: rgba(148, 226, 213, 0.15);
    color: {COLORS["teal"]};
    border: 1px solid rgba(148, 226, 213, 0.3);
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}}
#listenButton:hover {{
    background-color: rgba(148, 226, 213, 0.25);
}}
#listenButton:disabled {{
    color: {COLORS["overlay0"]};
    background-color: transparent;
    border-color: {COLORS["surface1"]};
}}

#listeningActiveButton {{
    background-color: rgba(249, 226, 175, 0.15);
    color: {COLORS["yellow"]};
    border: 1px solid rgba(249, 226, 175, 0.4);
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 600;
}}

/* ─── Inputs ────────────────────────────────────── */
QLineEdit {{
    background-color: {COLORS["mantle"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: {COLORS["lavender"]};
    selection-color: {COLORS["base"]};
}}
QLineEdit:focus {{
    border-color: {COLORS["lavender"]};
    background-color: {COLORS["crust"]};
}}
QLineEdit:disabled {{
    color: {COLORS["overlay0"]};
    background-color: {COLORS["surface0"]};
}}
QLineEdit#inputField {{
    background-color: {COLORS["mantle"]};
}}

QSpinBox {{
    background-color: {COLORS["mantle"]};
    color: {COLORS["text"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}}
QSpinBox:focus {{
    border-color: {COLORS["lavender"]};
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLORS["surface0"]};
    border: none;
    width: 18px;
    border-radius: 3px;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLORS["surface1"]};
}}

/* ─── Radio buttons ─────────────────────────────── */
QRadioButton {{
    color: {COLORS["text"]};
    font-size: 13px;
    spacing: 6px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid {COLORS["surface2"]};
    background-color: transparent;
}}
QRadioButton::indicator:checked {{
    border-color: {COLORS["lavender"]};
    background-color: {COLORS["lavender"]};
}}
QRadioButton::indicator:hover {{
    border-color: {COLORS["subtext0"]};
}}

/* ─── Checkboxes ────────────────────────────────── */
QCheckBox {{
    color: {COLORS["text"]};
    font-size: 13px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid {COLORS["surface2"]};
    background-color: transparent;
}}
QCheckBox::indicator:checked {{
    border-color: {COLORS["lavender"]};
    background-color: {COLORS["lavender"]};
    image: url(none);
}}
QCheckBox::indicator:hover {{
    border-color: {COLORS["subtext0"]};
}}

/* ─── Slider ────────────────────────────────────── */
QSlider::groove:horizontal {{
    background: {COLORS["surface1"]};
    height: 4px;
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: {COLORS["lavender"]};
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}
QSlider::handle:horizontal:hover {{
    background: #c6d0fe;
}}
QSlider::sub-page:horizontal {{
    background: {COLORS["lavender"]};
    border-radius: 2px;
}}

/* ─── Message boxes ─────────────────────────────── */
QMessageBox {{
    background-color: {COLORS["base"]};
}}
QMessageBox QLabel {{
    color: {COLORS["text"]};
}}

/* ─── Divider lines ─────────────────────────────── */
#divider {{
    background-color: {COLORS["surface0"]};
    max-height: 1px;
    min-height: 1px;
}}

/* ─── Dialog panels ─────────────────────────────── */
#dialogPanel {{
    background-color: {COLORS["mantle"]};
    border: 1px solid {COLORS["surface0"]};
    border-radius: 8px;
}}
#keyDisplayPanel {{
    background-color: {COLORS["surface0"]};
    border: 1px solid {COLORS["surface1"]};
    border-radius: 6px;
}}
"""
