@echo off
set "UVIE_ROOT=%~dp0"
set "R_HOME=%UVIE_ROOT%runtime\R"
set "R_LIBS_USER=%UVIE_ROOT%runtime\library"
cd /d "%UVIE_ROOT%"
if not exist "%R_HOME%\bin\Rscript.exe" (
  echo This is a source checkout, not a complete runtime package. Use the full Windows release.
  pause
  exit /b 1
)
"%R_HOME%\bin\Rscript.exe" --vanilla app.R
pause
