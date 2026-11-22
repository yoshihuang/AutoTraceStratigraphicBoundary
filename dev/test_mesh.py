exec(open("test_model3d.py", encoding="utf8").read().split("# surface agreement")[0])
from autotrace_strat_boundary.core import model_outputs as mo
cell = max(extent[2]-extent[0], extent[3]-extent[1]) / 90
t = time.time(); sol = mo.unit_solids(model, cell); print("solids %.1fs" % (time.time()-t), {units[k].code: len(f) for k, (v, f) in sol.items()})
# closedness check: every edge shared by exactly 2 faces
for k, (v, f) in sol.items():
    e = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
    _, c = np.unique(e, axis=0, return_counts=True)
    print("  ", units[k].code, "verts", len(v), "open edges", (c != 2).sum(), "zrange %.0f..%.0f" % (v[:, 2].min(), v[:, 2].max()))
t = time.time(); hz = mo.horizons(model, cell); print("horizons %.1fs" % (time.time()-t), [(units[b].code, units[a].code, len(f)) for s, b, a, l, v, f in hz])
fp = mo.fault_planes(model, cell); print("faults", [(f.name, len(fc)) for f, v, fc in fp])
tv, tf, tu = mo.terrain(model); print("terrain faces", len(tf), np.unique(tu, return_counts=True))
sec = mo.auto_section(model, 230)
t = time.time(); r = mo.section_raster(model, sec); print("section %.1fs" % (time.time()-t), r["U"].shape, "ztop", r["ztop"], "fault traces", len(r["faults"]), np.unique(r["U"], return_counts=True))
np.save("C:/Users/yoshi/AppData/Local/Temp/claude/8d0f89a79a92053f/d6c4e78e-7d5b-4a65-a153-6a1da43e165e/scratchpad/secU.npy", r["U"])
