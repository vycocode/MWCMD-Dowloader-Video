@echo off
title Instalador y Ejecutor de Aplicación Python

REM ==========================================================
REM 1. INSTALACIÓN DE DEPENDENCIAS
REM ==========================================================

echo.
echo ==========================================================
echo    Instalando dependencias de Python (puede tardar)...
echo ==========================================================
echo.

REM Intenta usar 'python -m pip' que es la forma mas robusta
python -m pip install selenium webdriver-manager Pillow tk

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: Fallo al instalar una o mas dependencias.
    echo Asegurese de que Python y pip estan instalados y accesibles.
    echo Presione cualquier tecla para salir...
    pause > nul
    exit /b 1
)

echo.
echo ✅ Instalacion de dependencias completa!

REM ==========================================================
REM 2. EJECUCION DEL SCRIPT PRINCIPAL
REM ==========================================================

echo.
echo ==========================================================
echo    Iniciando la aplicacion...
echo ==========================================================
echo.

REM Cambia "app.py" por el nombre real de tu archivo Python si es diferente
python app.py

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ ERROR: La aplicacion termino con un error.
    echo Presione cualquier tecla para salir...
    pause > nul
    exit /b 1
)

echo.
echo La aplicacion ha finalizado.
echo Presione cualquier tecla para salir...
pause > nul