# -*- coding: utf-8 -*-
import os

from qgis.core import QgsProcessingProvider
from qgis.PyQt.QtGui import QIcon

from ..i18n import tr
from .alg_geology import BuildGeologyAlgorithm
from .alg_trace import ICON_DIR, TraceBoundaryAlgorithm

PROVIDER_ID = "autotracestrat"


class AutoTraceStratProvider(QgsProcessingProvider):
    def id(self):
        return PROVIDER_ID

    def name(self):
        return tr("provider_name")

    def icon(self):
        return QIcon(os.path.join(ICON_DIR, "icon.svg"))

    def loadAlgorithms(self):  # noqa: N802
        self.addAlgorithm(TraceBoundaryAlgorithm())
        self.addAlgorithm(BuildGeologyAlgorithm())
