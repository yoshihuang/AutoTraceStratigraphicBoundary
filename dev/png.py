from qgis_env import *
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.PyQt.QtGui import QImage, QPainter
from qgis.PyQt.QtCore import Qt
d=os.path.join(os.path.dirname(HERE),"autotrace_strat_boundary","icons")
r=QSvgRenderer(os.path.join(d,"icon.svg")); img=QImage(128,128,QImage.Format.Format_ARGB32); img.fill(Qt.GlobalColor.transparent)
p=QPainter(img); r.render(p); p.end(); print(img.save(os.path.join(d,"icon.png")))
