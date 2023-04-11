@echo off
if exist "venv\" (
    venv\Scripts\mkdocs.exe serve
) else (
    python -m venv venv
    venv\Scripts\pip.exe install -r requirements.txt
    venv\Scripts\mkdocs.exe serve
)
