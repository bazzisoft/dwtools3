@echo off
echo "STOP NOW IF YOUR SOURCE TREE IS NOT CLEAN AND COMMITTED!!!"
pause

call venv\Scripts\activate.bat
autopep8 -i -r --select=W291,W293,W391,E261,E301,E302,E303,E122,E128 dwtools3
pause
