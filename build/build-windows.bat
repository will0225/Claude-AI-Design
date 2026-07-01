@echo off
REM Build HAM Report Studio for Windows (must run on a Windows PC)
cd /d "%~dp0\.."

echo === HAM Report Studio - Windows build ===

if not exist build\venv-build (
  echo Creating build virtual environment...
)

python -m venv build\venv-build
call build\venv-build\Scripts\activate.bat

python -m pip install -q --upgrade pip setuptools wheel
pip install -q -r python\requirements.txt
pip install -q -r python\requirements-build.txt

REM pywebview is optional (native embedded window)
pip install -q pywebview 2>nul
if errorlevel 1 (
  echo.
  echo Skipping pywebview - app will open in the default browser ^(fine for clients^).
)

pyinstaller build\report_studio.spec --noconfirm --clean

echo.
echo Built: dist\HAM Report Studio\HAM Report Studio.exe
echo Zip the entire "dist\HAM Report Studio" folder and send to the client.
echo.
pause
