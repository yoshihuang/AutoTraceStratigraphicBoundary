"""Build the zip to upload to https://plugins.qgis.org (python dev/package.py)."""
import configparser
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = "autotrace_strat_boundary"
SRC = os.path.join(ROOT, PKG)
EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}
EXCLUDE_EXT = {".pyc", ".pyo"}

meta = configparser.ConfigParser()
meta.read(os.path.join(SRC, "metadata.txt"), encoding="utf-8")
version = meta["general"]["version"]
for key in ("name", "qgisMinimumVersion", "description", "about", "version", "author", "email", "repository"):
    if not meta["general"].get(key):
        sys.exit("metadata.txt: missing %s" % key)
placeholders = [k for k in ("author", "email", "repository", "tracker", "homepage")
                if "YOUR" in meta["general"].get(k, "").upper() or "example.com" in meta["general"].get(k, "")]
if placeholders:
    print("WARNING: fill in metadata.txt before publishing:", ", ".join(placeholders))

errors = 0
for dp, dn, fn in os.walk(SRC):
    dn[:] = [d for d in dn if d not in EXCLUDE_DIRS]
    for f in fn:
        if f.endswith(".py"):
            try:
                with open(os.path.join(dp, f), encoding="utf-8") as fh:
                    compile(fh.read(), os.path.join(dp, f), "exec")
            except SyntaxError as e:
                print(e)
                errors += 1
if errors:
    sys.exit("syntax errors")

os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
out = os.path.join(ROOT, "dist", "%s-%s.zip" % (PKG, version))
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dp, dn, fn in os.walk(SRC):
        dn[:] = sorted(d for d in dn if d not in EXCLUDE_DIRS)
        for f in sorted(fn):
            if os.path.splitext(f)[1] in EXCLUDE_EXT:
                continue
            full = os.path.join(dp, f)
            z.write(full, os.path.relpath(full, ROOT).replace(os.sep, "/"))
print("built", out, "%.0f KB" % (os.path.getsize(out) / 1024.0))
