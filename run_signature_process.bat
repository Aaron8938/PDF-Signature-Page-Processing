@echo off
chcp 65001 >nul 2>&1
title PDF Signature Page Processing v1.0.0
setlocal EnableDelayedExpansion
set "PYTHONDONTWRITEBYTECODE=1"
color 0F

echo.
echo ===================================================
echo PDF Signature Page Processing v1.0.0
echo ===================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PY_FILE=%SCRIPT_DIR%main_signature_process.py"

if not exist "%PY_FILE%" (
    color 0C
    echo.
    echo  [Error] Script not found: %PY_FILE%
    echo.
    goto :EXIT
)

set "PYTHON=C:\Users\Administrator\.workbuddy\binaries\python\envs\pdfsig\Scripts\python.exe"

if not exist "%PYTHON%" (
    color 0C
    echo.
    echo  [Error] Python runtime not found: %PYTHON%
    echo.
    goto :EXIT
)

REM Build args inside if block, but call Python OUTSIDE (stdin works normally)
set "PY_ARGS="
if not "%~1"=="" (
    echo ---------------------------------------------------
    echo  Processing: drag-dropped file(s)
    echo  Please wait, do not close this window...
    echo ---------------------------------------------------
    echo.
    set "ALL_ARGS="
    :loop_args
    if "%~1"=="" goto end_args
    set "ARG=%~1"
    set "ARG=!ARG:"=!"
    set "ALL_ARGS=!ALL_ARGS! "!ARG!""
    shift
    goto loop_args
    :end_args
    set "PY_ARGS=!ALL_ARGS!"
)

"%PYTHON%" "%PY_FILE%" !PY_ARGS!

set "RET=!ERRORLEVEL!"
echo.
if "!RET!"=="0" (
    powershell -NoProfile -Command "Write-Host '[Success] Processing completed.'"
) else (
    color 0C
    powershell -NoProfile -Command "Write-Host '[Error] Processing finished with errors. Please check logs above.'"
)

:EXIT
echo.
powershell -NoProfile -Command "$r = Read-Host 'Press [Y] to run again, or [Enter] to exit'; if ($r -eq 'y' -or $r -eq 'yes') { Start-Process -FilePath '%~f0' }"
exit
