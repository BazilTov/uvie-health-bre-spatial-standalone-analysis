"""Maintainer build helper for native Windows/Mac/Linux release runners.

Requires an already-installed R environment. Platform execution tests remain
mandatory; copying files alone does not prove a bundle is portable.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
runtime = ROOT / 'runtime'
source = Path((runtime / 'build-r-home.txt').read_text().strip())
destination = runtime / 'R'
shutil.copytree(source,destination,symlinks=False,dirs_exist_ok=True)
library = runtime / 'library'
library.mkdir(exist_ok=True)
for location in (runtime / 'build-library-paths.txt').read_text().splitlines():
    base = Path(location)
    for package in base.iterdir():
        if package.is_dir() and (package / 'DESCRIPTION').is_file():
            shutil.copytree(package,library/package.name,symlinks=False,dirs_exist_ok=True)
if os.name != 'nt':
    wrapper = destination / 'bin/R'
    text = wrapper.read_text()
    text = re.sub(r'^R_HOME_DIR=.*$', 'R_HOME_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"', text, count=1, flags=re.M)
    text = re.sub(r'^R_SHARE_DIR=.*$', 'R_SHARE_DIR="$R_HOME_DIR/share"', text, flags=re.M)
    text = re.sub(r'^R_INCLUDE_DIR=.*$', 'R_INCLUDE_DIR="$R_HOME_DIR/include"', text, flags=re.M)
    text = re.sub(r'^R_DOC_DIR=.*$', 'R_DOC_DIR="$R_HOME_DIR/doc"', text, flags=re.M)
    text = text.replace('# Shell wrapper for R executable.', '# Shell wrapper for R executable.\n# Relocated by UVIE Spatial.\nDYLD_LIBRARY_PATH="$(CDPATH= cd -- "$(dirname -- "$0")/../lib" && pwd)${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"\nexport DYLD_LIBRARY_PATH')
    wrapper.write_text(text)
    (ROOT / 'launch.command').chmod(0o755)
if os.sys.platform.startswith('linux'):
    # Bundle non-glibc shared libraries used by R and its installed packages.
    native = runtime / 'native-lib'; native.mkdir(exist_ok=True)
    pending = [destination / 'bin/exec/R'] + list(destination.rglob('*.so')) + list(library.rglob('*.so'))
    seen = set()
    while pending:
        binary = pending.pop()
        result = subprocess.run(['ldd',str(binary)],capture_output=True,text=True)
        for path in re.findall(r'=> (/[^ ]+)',result.stdout):
            dep = Path(path)
            if dep.name.startswith(('libc.so','libm.so','libpthread.so','libdl.so','librt.so')):
                continue
            if dep.name in seen:
                continue
            seen.add(dep.name)
            shutil.copy2(dep,native/dep.name)
            pending.append(dep)
print('Runtime copied. Execute the full app and benchmark tests before publishing.')
