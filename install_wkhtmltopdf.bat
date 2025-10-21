@echo off
echo Installing wkhtmltopdf for Windows...

REM Download and install wkhtmltopdf
echo Downloading wkhtmltopdf...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox-0.12.6-1.msvc2015-win64.exe' -OutFile 'wkhtmltopdf-installer.exe'"

echo Installing wkhtmltopdf...
wkhtmltopdf-installer.exe /S

echo Adding to PATH...
setx PATH "%PATH%;C:\Program Files\wkhtmltopdf\bin" /M

echo Installation complete!
echo Please restart your command prompt to use wkhtmltoimage
pause