@echo off
REM Build HAM Report Studio for Windows (run on Windows)
cd /d "%~dp0\.."

echo === HAM Report Studio - Windows build ===

python -m venv build\venv-build
call build\venv-build\Scripts\activate.bat
pip install -q -r python\requirements.txt -r python\requirements-build.txt

pyinstaller build\report_studio.spec --noconfirm --clean

echo.
echo Built: dist\HAM Report Studio\HAM Report Studio.exe
echo Zip the dist\HAM Report Studio folder and send to the client.
pause
