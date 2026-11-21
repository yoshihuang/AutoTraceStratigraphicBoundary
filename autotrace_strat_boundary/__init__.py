# -*- coding: utf-8 -*-
"""AutoTrace Stratigraphic Boundary - QGIS plugin entry point."""


def classFactory(iface):  # noqa: N802 (QGIS API name)
    from .plugin import AutoTraceStratBoundaryPlugin

    return AutoTraceStratBoundaryPlugin(iface)
