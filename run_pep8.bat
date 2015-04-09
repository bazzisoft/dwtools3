@echo off
call venv\Scripts\activate.bat
pep8 dwtools3 -r --max-line-length=140 --ignore=E221,E241,E265 --exclude=_docs > __pep8.txt

