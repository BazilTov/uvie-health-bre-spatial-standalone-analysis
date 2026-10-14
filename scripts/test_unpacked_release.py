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
    env.update(UVIE_OPEN_BROWSER='0', UVIE_PORT='8767',
               R_HOME=str(app / 'runtime/R'), R_LIBS_USER=str(app / 'runtime/library'))
    command = ['cmd.exe', '/c', str(app / 'launch.bat')] if os.name == 'nt' else [str(app / 'launch.command')]
    with (output / 'launcher.log').open('w') as log:
        process = subprocess.Popen(command, cwd=app, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            test_env = os.environ.copy()
            test_env['UVIE_TEST_URL'] = 'http://127.0.0.1:8767'
            subprocess.run([shutil.which('node'), str(root / 'tests/check_app.mjs'), str(output)],
                           cwd=app, env=test_env, check=True, timeout=1500)
        finally:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
            else:
                process.terminate()
            process.wait(timeout=30)
