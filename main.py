#!/usr/bin/env python3
"""OSCApp — slide remote → OSC bridge."""

import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from app.config import AppConfig
from app.main_window import MainWindow
from app.theme import STYLESHEET


def main() -> None:
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("OSCApp")
    app.setOrganizationName("OSCApp")
    app.setApplicationDisplayName("OSCApp")
    app.setStyleSheet(STYLESHEET)

    config = AppConfig.load_default()
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
