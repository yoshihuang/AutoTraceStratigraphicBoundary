# -*- coding: utf-8 -*-
"""Save the bundled sample project (C19 oblique-slip fault) to a user folder."""
import os
import zipfile

from qgis.core import QgsSettings
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

from .i18n import tr

PLUGIN_DIR = os.path.dirname(__file__)
SAMPLE_ZIP = os.path.join(PLUGIN_DIR, "data", "c19_sample.zip")
LAST_DIR_KEY = "AutoTraceStratBoundary/sampleDir"


def _yes_no(parent, text):
    btn = QMessageBox.StandardButton
    r = QMessageBox.question(parent, tr("plugin_name"), text, btn.Yes | btn.No, btn.Yes)
    return r == btn.Yes


def extract_sample(target_dir, overwrite=True):
    """Extract the sample zip into *target_dir*; return the path of the .qgz project."""
    project = None
    with zipfile.ZipFile(SAMPLE_ZIP) as z:
        root = os.path.realpath(target_dir)
        for info in z.infolist():
            dest = os.path.realpath(os.path.join(root, info.filename))
            if not dest.startswith(root + os.sep):  # zip-slip guard
                continue
            if info.is_dir():
                os.makedirs(dest, exist_ok=True)
                continue
            if os.path.exists(dest) and not overwrite:
                pass
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                with z.open(info) as src, open(dest, "wb") as out:
                    out.write(src.read())
            if dest.lower().endswith((".qgz", ".qgs")):
                project = dest
    return project


def sample_root_name():
    with zipfile.ZipFile(SAMPLE_ZIP) as z:
        first = z.namelist()[0]
    return first.split("/")[0]


def download_sample_dialog(iface):
    parent = iface.mainWindow()
    settings = QgsSettings()
    start = settings.value(LAST_DIR_KEY, os.path.expanduser("~"))
    folder = QFileDialog.getExistingDirectory(parent, tr("sample_choose_dir"), start)
    if not folder:
        return
    settings.setValue(LAST_DIR_KEY, folder)
    target = os.path.join(folder, sample_root_name())
    if os.path.exists(target) and not _yes_no(parent, tr("sample_exists", path=target)):
        return
    try:
        project = extract_sample(folder)
    except Exception as e:  # disk full, permission ...
        QMessageBox.critical(parent, tr("plugin_name"), tr("sample_error", err=e))
        return
    if project and _yes_no(parent, tr("sample_done", path=target)):
        if iface.newProject(True):  # asks to save the current project first
            iface.addProject(project)
