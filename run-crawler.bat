@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\ziiji\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
set "LOG_FILE=%PROJECT_DIR%crawler-log.txt"

pushd "%PROJECT_DIR%"

echo ================================================== >> "%LOG_FILE%"
echo [%date% %time%] Starting crawler.py >> "%LOG_FILE%"

"%PYTHON_EXE%" "%PROJECT_DIR%crawler.py" >> "%LOG_FILE%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"

echo [%date% %time%] crawler.py finished with exit code %EXIT_CODE% >> "%LOG_FILE%"
echo. >> "%LOG_FILE%"

popd
endlocal
