@echo off
REM Run this script with administrator rights.
REM Requires Chocolatey: https://chocolatey.org/install

REM Install system dependencies
choco install -y tesseract poppler

REM Upgrade pip and install Python packages
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

