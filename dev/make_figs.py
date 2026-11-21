from qgis_env import *
import math, numpy as np
from qgis.core import QgsVectorLayer, QgsGeometry, QgsRectangle
from autotrace_strat_boundary.core.tracer import BoundaryTracer, DemGrid, OutcropPoint, blended_surface, zero_contours
from autotrace_strat_boundary.core.geology_builder import GeologyBuilder, BoundaryLine
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = os.path.join(os.path.dirname(HERE), "autotrace_strat_boundary", "help", "img")
L = lambda n: QgsVectorLayer(GPKG + "|layername=" + n, n, "ogr")
dem = DemGrid(DEM)
arr, gt = dem.read_window(dem.extent)
ny, nx = arr.shape
xs = gt[0] + (np.arange(nx)+.5)*gt[1]; ys = gt[3] + (np.arange(ny)+.5)*gt[5]
X, Y = np.meshgrid(xs, ys)
faults = [f.geometry() for f in L("faults").getFeatures()]
P = {f.id(): f for f in L("Stratigraphic_Boundary").getFeatures()}
def op(f): 
    p=f.geometry().asPoint(); return OutcropPoint(f.id(), p.x(), p.y(), f["dip"], f["dip_dir"], f["unit_code_u"], f["unit_code_d"], f["overturned"])
def lines(ax, g, **kw):
    for part in (g.asGeometryCollection() if g.isMultipart() else [g]):
        if part.type()==1:
            xy=part.asPolyline(); ax.plot([p.x() for p in xy],[p.y() for p in xy],**kw)
COL={"O5":"#d62728","O4":"#ff7f0e","O3":"#2ca02c","O2":"#1f77b4","O1":"#9467bd"}
def strike_symbol(ax, p, size=40):
    a=math.radians(p.dip_dir); sx,sy=math.cos(a),-math.sin(a)  # strike = dipdir-90
    ax.plot([p.x-sx*size,p.x+sx*size],[p.y-sy*size,p.y+sy*size],"k-",lw=2)
    ax.plot([p.x,p.x+math.sin(a)*size*.5],[p.y,p.y+math.cos(a)*size*.5],"k-",lw=2)
    ax.text(p.x+math.sin(a)*size*.9,p.y+math.cos(a)*size*.9,"%d°"%p.dip,fontsize=9,ha="center",va="center",fontweight="bold")

# ---- fig1: structure contour method for one point
p = op(P[11]); p.z = dem.sample(p.x,p.y)
w = 380; win=(p.x-w,p.x+w,p.y-w,p.y+w)
fig, ax = plt.subplots(figsize=(7,7))
m=(X>win[0])&(X<win[1])
cs=ax.contour(X,Y,arr,levels=np.arange(160,330,10),colors="#8c6d31",linewidths=.6)
ax.clabel(cs,fmt="%d",fontsize=7)
plane=blended_surface(X,Y,[p])
cs2=ax.contour(X,Y,plane,levels=np.arange(160,330,10),colors="#1f77b4",linewidths=1,linestyles="--")
ax.clabel(cs2,fmt="%d",fontsize=7,colors="#1f77b4")
# intersections: cells where dem contour level == plane contour level
for lev in np.arange(160,330,10):
    a=arr-lev; b=plane-lev
    for g in zero_contours(a,gt):
        for h in zero_contours(b,gt):
            i=g.intersection(h)
            if not i.isEmpty():
                for q in (i.asGeometryCollection() if i.isMultipart() else [i]):
                    if q.type()==0: 
                        pt=q.asPoint()
                        if win[0]<pt.x()<win[1] and win[2]<pt.y()<win[3]: ax.plot(pt.x(),pt.y(),"o",color="#d62728",ms=5,zorder=5)
for g in zero_contours(arr-plane,gt): lines(ax,g,color="#d62728",lw=2.2)
strike_symbol(ax,p)
ax.plot(p.x,p.y,"k^",ms=9,zorder=6)
ax.set_xlim(win[0],win[1]); ax.set_ylim(win[2],win[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig1_structure_contours.png"),dpi=90); plt.close(fig)

# ---- fig2: profile along dip direction through the point
a=math.radians(p.dip_dir); s=np.linspace(-450,450,400)
px=p.x+s*math.sin(a); py=p.y+s*math.cos(a)
topo=np.array([dem.sample(x,y) or np.nan for x,y in zip(px,py)])
pl=p.z - math.tan(math.radians(p.dip))*s
fig,ax=plt.subplots(figsize=(8,3.4))
ax.fill_between(s,pl,topo,where=topo>pl,color="#f4a582",alpha=.8,interpolate=True)
ax.fill_between(s,np.minimum(topo,pl),120,color="#92c5de",alpha=.8)
ax.plot(s,topo,"k-",lw=1.5); ax.plot(s,pl,"--",color="#1f77b4",lw=1.5)
sign=np.sign(topo-pl); idx=np.where(np.diff(sign)!=0)[0]
for i in idx: ax.plot(s[i],topo[i],"o",color="#d62728",ms=7,zorder=5)
ax.plot(0,p.z,"k^",ms=9); ax.set_ylim(120,360); ax.set_xlim(-450,450)
ax.text(-430,345,"NE",fontsize=9); ax.text(400,345,"SW",fontsize=9)
ax.set_xlabel("m"); ax.set_ylabel("m")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig2_profile.png"),dpi=90); plt.close(fig)

# ---- fig3: whole map, blended traces + faults
pts=[op(f) for f in P.values()]
res=BoundaryTracer(dem,faults,connect_gap=100).run(pts)
fig,ax=plt.subplots(figsize=(7.5,7.5))
ax.imshow(arr,extent=(gt[0],gt[0]+gt[1]*nx,gt[3]+gt[5]*ny,gt[3]),cmap="gist_earth",alpha=.35)
cs=ax.contour(X,Y,arr,levels=np.arange(160,330,20),colors="#8c6d31",linewidths=.4)
for r in res: lines(ax,r.geom,color=COL[r.upper],lw=2)
for g in faults: lines(ax,g,color="k",lw=2.5)
for q in pts: ax.plot(q.x,q.y,"o",color=COL[q.upper],mec="k",ms=6,zorder=5)
ax.set_xlim(250000,252000); ax.set_ylim(2650000,2652000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig3_traced.png"),dpi=90); plt.close(fig)

# ---- fig4: geology built from traced lines + bedding
bed=[(f.geometry().asPoint(),f["unit_code"]) for f in L("bedding").getFeatures()]
from autotrace_strat_boundary.core.geom_utils import line_parts
gs={f["unit_code"]: f.geometry() for f in L("geology").getFeatures()}
edited=[]
for u,d in [("O5","O4"),("O4","O3"),("O3","O2"),("O2","O1")]:
    for q in line_parts(gs[u].intersection(gs[d]).mergeLines()): edited.append(BoundaryLine(q,u,d,""))
polys=GeologyBuilder(dem.extent,5,100).build(edited,faults,bed)
FC={"O5":"#f4a582","O4":"#fddbc7","O3":"#d1e5f0","O2":"#92c5de","O1":"#b8e186"}
fig,ax=plt.subplots(figsize=(7.5,7.5))
for pg in polys:
    for part in (pg.geom.asGeometryCollection() if pg.geom.isMultipart() else [pg.geom]):
        ring=part.asPolygon()[0]; ax.fill([v.x() for v in ring],[v.y() for v in ring],color=FC.get(pg.unit,"#cccccc"),ec="#555",lw=.4)
        c=part.pointOnSurface().asPoint()
        if part.area()>20000: ax.text(c.x(),c.y(),pg.unit or "?",ha="center",fontsize=10,fontweight="bold")
for g in faults: lines(ax,g,color="k",lw=2.5)
ax.set_xlim(250000,252000); ax.set_ylim(2650000,2652000); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig4_geology.png"),dpi=90); plt.close(fig)
print("ok")
