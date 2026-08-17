@echo off
setlocal
cd /d "%~dp0"
if not exist "model_bundle.pkl" (
  echo ERROR: model_bundle.pkl is missing from %CD%
  pause
  exit /b 1
)
echo Starting the Gallbladder Cancer Dynamic Survival Nomogram...
echo Open http://127.0.0.1:8010 in your browser.
python -m shiny run --host 127.0.0.1 --port 8010 app.py
endlocal
