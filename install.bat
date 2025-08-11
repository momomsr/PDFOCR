@echo off
REM Run this script with administrator rights.
REM Installs Tesseract on Windows.  The script first tries to
REM use Chocolatey and falls back to Winget.  If neither package manager is
REM available, a short manual installation hint is shown.

REM --- install system dependencies ---------------------------------------
where choco >NUL 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Installing dependencies via Chocolatey...
    choco install -y tesseract
) else (
    where winget >NUL 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo Installing dependencies via Winget...
        winget install -e --id UB-Mannheim.Tesseract-OCR
    ) else (
        echo Neither Chocolatey nor Winget could be found.
        echo Downloading Tesseract installer...
        set DOWNLOAD_URL=https://github.com/UB-Mannheim/tesseract/releases/latest/download/tesseract-ocr-w64-setup.exe
        powershell -Command "Invoke-WebRequest -Uri %DOWNLOAD_URL% -OutFile tesseract-installer.exe"
        if exist tesseract-installer.exe (
            echo Installing Tesseract...
            start /wait tesseract-installer.exe /SILENT
            del tesseract-installer.exe
        ) else (
            echo Failed to download Tesseract installer.
            echo Please install Tesseract manually:
            echo   https://github.com/UB-Mannheim/tesseract/wiki
            pause
        )
    )
)

REM --- install python dependencies --------------------------------------
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

