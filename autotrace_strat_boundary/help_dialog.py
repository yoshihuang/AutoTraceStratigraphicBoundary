# -*- coding: utf-8 -*-
"""Principle & user-guide viewer (HTML per language under help/<lang>/)."""
import os

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtGui import QDesktopServices
from qgis.PyQt.QtWidgets import QDialog, QHBoxLayout, QPushButton, QTextBrowser, QVBoxLayout

from .i18n import current_language, tr

HELP_DIR = os.path.join(os.path.dirname(__file__), "help")


def help_file(lang=None):
    lang = lang or current_language()
    path = os.path.join(HELP_DIR, lang, "index.html")
    if not os.path.exists(path):
        path = os.path.join(HELP_DIR, "en", "index.html")
    return path


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("help_title"))
        self.resize(980, 760)
        self.path = help_file()

        browser = QTextBrowser(self)
        browser.setOpenExternalLinks(True)
        browser.setSearchPaths([os.path.dirname(self.path), HELP_DIR])
        browser.setSource(QUrl.fromLocalFile(self.path))

        open_btn = QPushButton(tr("help_browser"), self)
        open_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(self.path)))
        close_btn = QPushButton(tr("close"), self)
        close_btn.clicked.connect(self.accept)

        buttons = QHBoxLayout()
        buttons.addWidget(open_btn)
        buttons.addStretch(1)
        buttons.addWidget(close_btn)
        layout = QVBoxLayout(self)
        layout.addWidget(browser)
        layout.addLayout(buttons)
