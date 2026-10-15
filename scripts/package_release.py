"""Package a preinstalled R environment. Build-time Python only; users need none.

Copies the repository's already-tested runtime into a complete release archive.
Never downloads dependencies or labels an untested platform validated.
"""
import argparse
import hashlib
import json
import os
import platform
import stat
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ['app.R', 'processed_input.R', 'PROCESSED-INPUT.md', 'launch.command', 'launch.bat', 'README.md', 'LICENSE',
          'THIRD_PARTY.md', 'VALIDATION.md', 'scripts/run_reference.R',
          'benchmarks/kidney_raw_checkpoint.csv', 'benchmarks/input-reconciliation.json',
          'benchmarks/full-import-agreement.json', 'benchmarks/q3-arithmetic-agreement.json']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    runtime = ROOT / 'runtime'
    if not (runtime / 'R').is_dir() or not (runtime / 'library').is_dir():
        raise SystemExit('Missing preinstalled runtime; refusing an incomplete full package')
    manifest = runtime / 'package-versions.csv'
    if not manifest.exists():
        raise SystemExit('Runtime package-version manifest missing')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    entries = [ROOT / name for name in SOURCE]
    entries += [p for p in runtime.rglob('*') if p.is_file()]
    digest = hashlib.sha256()
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(entries):
            relative = path.relative_to(ROOT)
            # Preserve executable modes; symlinks are materialized for ZIP portability.
            info = zipfile.ZipInfo(str(Path('UVIE-Spatial') / relative))
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = path.stat().st_mode
            if relative.name == 'launch.command':
                mode |= stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
            info.external_attr = mode << 16
            content = path.read_bytes()
            archive.writestr(info, content)
            digest.update(str(relative).encode() + b'\0' + hashlib.sha256(content).digest())
    summary = {'platform': platform.system(), 'architecture': platform.machine(),
               'archive_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest(),
               'content_manifest_sha256': digest.hexdigest(), 'files': len(entries),
               'scope': 'This platform only; see VALIDATION.md for executed checks'}
    args.output.with_suffix('.manifest.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
