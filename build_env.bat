@echo off
echo Delete and rebuild the virtual environment?
pause
rmdir /s /q venv
call ..\..\environments\python3.4\virtualenv.bat venv
call venv\Scripts\activate.bat

pip install sphinx
pip install django
pip install pep8
pip install autopep8
pip install pylint

pause