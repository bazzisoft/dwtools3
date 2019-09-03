@echo off
setlocal
call venv\Scripts\activate.bat
cd dwtools3/_docs
rem rmdir /s /q build
call make.bat html
cd ..\..

pause