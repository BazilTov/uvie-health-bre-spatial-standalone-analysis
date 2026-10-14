"""Promote exact tested ZIP bytes; never rebuild or alter bundled packages."""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

source, output = map(Path, sys.argv[1:3])
output.mkdir(parents=True, exist_ok=True)
names = {'macos-14': 'Mac-AppleSilicon', 'macos-15-intel': 'Mac-Intel',
         'windows-2022': 'Windows-x64', 'ubuntu-22.04': 'Linux-Ubuntu22.04-x64'}
verified = []
for runner, label in names.items():
    matches = list(source.rglob(f'UVIE-Spatial-{runner}.zip'))
    if len(matches) != 1:
        raise SystemExit(f'Expected exactly one tested package for {runner}')
    package = matches[0]
    manifest = json.loads(package.with_suffix('.manifest.json').read_text())
    digest = hashlib.file_digest(package.open('rb'), 'sha256').hexdigest()
    if digest != manifest['archive_sha256']:
        raise SystemExit(f'Package checksum mismatch: {runner}')
    with zipfile.ZipFile(package) as archive:
        bad = archive.testzip()
        if bad:
            raise SystemExit(f'Corrupt ZIP entry: {bad}')
        if 'UVIE-Spatial/app.R' not in archive.namelist():
            raise SystemExit(f'Missing application: {runner}')
    destination = output / f'UVIE-Health-BRE-Spatial-Standalone-v0.2.0-{label}.zip'
    shutil.copyfile(package, destination)
    manifest['download_filename'] = destination.name
    destination.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2))
    checks = json.loads((package.parent / 'unpacked-checks/app-checks.json').read_text())
    if checks['status'] != 'pass':
        raise SystemExit(f'Unpacked-package evidence did not pass: {runner}')
    verified.append({'runner': runner, 'file': destination.name, 'sha256': digest, 'checks': checks})

root = Path(__file__).resolve().parents[1]
shutil.copyfile(root / 'DOWNLOAD-AND-LAUNCH.md', output / 'DOWNLOAD-AND-LAUNCH.md')
shutil.copyfile(root / 'VALIDATION.md', output / 'VALIDATION.md')
(output / 'PACKAGE-VERIFICATION.json').write_text(json.dumps({
    'tested_commit': 'a62687629a36f1b787a75fc657f63b51fb9ff3f0',
    'tested_run': 'https://github.com/BazilTov/uvie-health-bre-spatial-standalone-analysis/actions/runs/38638835108',
    'packages': verified,
    'scope': 'Native application, reference checkpoints, exports, and unpacked-ZIP checks; biological validation is separate.'
}, indent=2))
lines = []
for path in sorted(output.iterdir()):
    if path.is_file():
        with path.open('rb') as file:
            lines.append(f'{hashlib.file_digest(file, "sha256").hexdigest()}  {path.name}')
(output / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n')
print('Four complete packages verified; release assets prepared.')
