@echo off
echo Delete and rebuild the virtual environment?
pause
rmdir /s /q venv
call ..\..\environments\python3.7\virtualenv.bat venv
call venv\Scripts\activate.bat
pip install -r requirements.txt

pause