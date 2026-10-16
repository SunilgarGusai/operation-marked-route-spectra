@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (echo ERROR: Python was not found. & pause & exit /b 1)
python run_proofs.py
if errorlevel 1 (echo Mathematical verification FAILED & pause & exit /b 1)
python tests\check_reported_statistics.py
if errorlevel 1 (echo Numerical-summary verification FAILED & pause & exit /b 1)
python scriptsalidate_public_artifact.py
if errorlevel 1 (echo Repository validation FAILED & pause & exit /b 1)
echo COMPLETE: mathematical and artifact checks passed.
pause
