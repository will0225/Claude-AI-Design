@echo off
REM Build HAM Report Studio for Windows (must run on a Windows PC)
cd /d "%~dp0\.."

echo === HAM Report Studio - Windows build ===

python -m venv build\venv-build
call build\venv-build\Scripts\activate.bat

python -m pip install -q --upgrade pip setuptools wheel
pip install -q -r python\requirements.txt
pip install -q -r python\requirements-build.txt

pip install -q pywebview 2>nul

pyinstaller build\report_studio.spec --noconfirm --clean

copy /Y build\WINDOWS_READ_FIRST.txt "dist\HAM Report Studio\READ FIRST.txt"

echo.
echo SUCCESS: dist\HAM Report Studio\
echo.
echo IMPORTANT: Zip the ENTIRE folder "HAM Report Studio"
echo            (must include _internal\ and the .exe together)
echo.
pause
