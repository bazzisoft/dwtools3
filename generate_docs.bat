@echo off
setlocal
call venv\Scripts\activate.bat

set DJANGO_SETTINGS_MODULE=django.conf.global_settings


cd dwtools3/_docs
rem rmdir /s /q build
call make.bat html
cd ..\..

pause