@echo off
rem Preview the site with live reload, at http://127.0.0.1:8000/ by default.
rem Arguments go to "mkdocs serve", for example: serve.bat -a 127.0.0.1:8001
rem Creates venv\ on first use, and installs requirements.txt every time (quick
rem when nothing changed), so the venv follows that file.
if not exist "venv\" python -m venv venv
venv\Scripts\pip.exe install -q -r requirements.txt || exit /b 1
rem --livereload: with click 8.2 or later, MkDocs 1.6 turns it off unless given.
venv\Scripts\mkdocs.exe serve --livereload %*
