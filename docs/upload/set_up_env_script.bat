@echo off

>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
goto UACPrompt
) else ( goto gotAdmin )
:UACPrompt
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
"%temp%\getadmin.vbs"
exit /B
:gotAdmin
if exist "%temp%\getadmin.vbs" ( del "%temp%\getadmin.vbs" )
pushd "%CD%"
cd /D "%~dp0"

python --version | findstr "3\.[0-7].*" > nul && (goto python_installed)


ver|findstr "[3-5]\.[0-9]\.[0-9][0-9]*" > nul && (goto isBelowNT6)

echo Downloading Python

aria2c.exe -o python-3.6.4.exe https://www.python.org/ftp/python/3.6.4/python-3.6.4.exe

echo Installing Python
python-3.6.4.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

python.exe --version | find "3.6.4" > NUL && goto succeed36

python.exe --version | find "3.6.4" > NUL && goto succeed36

echo ....
echo Installing Python failed
echo ...
goto exit

:succeed36

echo Installing packages

C:\Python36\Scripts\pip.exe install requests
C:\Python36\Scripts\pip.exe install mutagen
C:\Python36\Scripts\pip.exe install pycryptodomex

echo Installation finished

goto exit

rem -----------------------------------------------------------

rem 一般来说，除了极少数情况，XP一般都是x86的
:isBelowNT6 

echo Downloading Python

aria2c.exe -o python-3.4.4.msi https://www.python.org/ftp/python/3.4.4/python-3.4.4.msi

echo Installing Python

msiexec /i .\python-3.4.4.msi /quiet /qn

C:\Python34\python.exe --version | find "3.4.4" > NUL goto succeed34

echo ....
echo Installing Python failed
echo ...
goto exit

:succeed34

echo Installing packages

C:\Python34\Scripts\pip.exe install requests
C:\Python34\Scripts\pip.exe install mutagen
C:\Python34\Scripts\pip.exe install pycryptodomex

echo
echo
echo ...
echo Installation finished
echo ...

goto exit

:python_installed
echo Python has been already installed

where python > temp
set /p python_path=<temp
del temp

cd /d %python_path:~0,-10%

cd /d Scripts

echo Installing packages

pip.exe install requests
pip.exe install mutagen
pip.exe install pycryptodomex

echo ...
echo Installation finished
echo ... 

goto exit
:exit

echo Press any key to exit
@pause