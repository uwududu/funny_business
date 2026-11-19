@echo off
cd /d "%~dp0"

:: Inicia o tradutor gráfico sem deixar console aberto
start "" pythonw traduzir_log.py 2>nul
if %ERRORLEVEL% EQU 0 exit

:: Fallback caso pythonw não esteja no PATH
python traduzir_log.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Nao foi possivel iniciar traduzir_log.py.
    echo.
    pause
)

