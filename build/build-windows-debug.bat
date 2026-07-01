@echo off
REM Debug build — shows console with error messages
cd /d "%~dp0\.."

python -m venv build\venv-build
call build\venv-build\Scripts\activate.bat
pip install -q -r python\requirements.txt -r python\requirements-build.txt

pyinstaller build\report_studio_debug.spec --noconfirm --clean

echo.
echo Run: dist\HAM Report Studio Debug\HAM Report Studio Debug.exe
echo A black console window will show any errors.
pause
