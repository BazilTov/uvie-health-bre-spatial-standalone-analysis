"""Test the actual release ZIP from a separate directory, using bundled R."""
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
archive = Path(sys.argv[1]).resolve()
output = root / 'output/unpacked-checks'
output.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='UVIE Unpacked Release ', ignore_cleanup_errors=(os.name == 'nt')) as folder:
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(folder)
        for info in bundle.infolist():
            mode = info.external_attr >> 16
            if mode and os.name != 'nt':
                (Path(folder) / info.filename).chmod(mode & 0o777)
    app = Path(folder) / 'UVIE-Spatial'
    env = os.environ.copy()
    test_port = os.environ.get('UVIE_UNPACKED_PORT', '8767')
    env.update(UVIE_OPEN_BROWSER='0', UVIE_PORT=test_port,
               R_HOME=str(app / 'runtime/R'), R_LIBS_USER=str(app / 'runtime/library'))
    command = ['cmd.exe', '/c', str(app / 'launch.bat')] if os.name == 'nt' else [str(app / 'launch.command')]
    with (output / 'launcher.log').open('w') as log:
        process = subprocess.Popen(command, cwd=app, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            test_env = os.environ.copy()
            test_env['UVIE_TEST_URL'] = 'http://127.0.0.1:' + test_port
            subprocess.run([shutil.which('node'), str(root / 'tests/check_app.mjs'), str(output)],
                           cwd=app, env=test_env, check=True, timeout=1500)
            fixture = root / 'output/spatial-input'
            if not (fixture / 'visium-spatial.zip').exists():
                raise RuntimeError('Public spatial fixture is required to verify the unpacked package')
            subprocess.run([shutil.which('node'), str(root / 'tests/check_spatial_app.mjs'), str(fixture)],
                           cwd=app, env=test_env, check=True, timeout=180)
            subprocess.run([sys.executable, str(root / 'tests/check_public_neighbors.py'), str(fixture)],
                           cwd=app, env=test_env, check=True, timeout=180)
            research = root / 'output/research-input'
            if not (research / 'research-fixture.zip').exists():
                raise RuntimeError('Research-analysis fixture is required to verify the unpacked package')
            subprocess.run([shutil.which('node'), str(root / 'tests/check_research_app.mjs'), str(research)],
                           cwd=app, env=test_env, check=True, timeout=180)
            subprocess.run([sys.executable, str(root / 'tests/check_research_exports.py'), str(research)],
                           cwd=app, env=test_env, check=True, timeout=60)
        finally:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            else:
                process.terminate()
            process.wait(timeout=30)
