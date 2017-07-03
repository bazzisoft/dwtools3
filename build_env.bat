@echo off
echo Delete and rebuild the virtual environment?
pause
rmdir /s /q venv
call ..\..\environments\python3.4\virtualenv.bat venv
call venv\Scripts\activate.bat

pip install sphinx
pip install sphinx-rtd-theme
pip install "django>=1.8,<1.9"
pip install pep8
pip install autopep8
pip install pylint
pip install openpyxl
pip install PyExcelerate
pip install pypiwin32
pip install simple-salesforce

pause