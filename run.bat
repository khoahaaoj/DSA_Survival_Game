@echo off
title Khởi động DSA Survival Game
color 0A
chcp 65001 > nul

echo ========================================================
echo        ⚔️  DSA SURVIVAL GAME - UIT  ⚔️
echo ========================================================
echo.

:: 1. Kiem tra Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [LOI] Khong tim thay Python tren may cua ban!
    echo Vui long cai dat Python 3.10 tro len tai: https://www.python.org/
    echo Nho tich chon "Add Python to PATH" khi cai dat.
    echo.
    pause
    exit /b 1
)

:: 2. Kiem tra / Tao Virtual Environment
if not exist "venv" (
    echo [*] Dang khoi tao moi truong ao (Virtual Environment)...
    python -m venv venv
    if %errorlevel% neq 0 (
        color 0C
        echo [LOI] Khong the tao virtual environment!
        pause
        exit /b 1
    )
)

:: 3. Kich hoat moi truong ao
call venv\Scripts\activate.bat

:: 4. Kiem tra & Cai dat dependencies
echo [*] Dang kiem tra thu vien game (Pygame)...
python -c "import pygame" >nul 2>nul
if %errorlevel% neq 0 (
    echo [*] Dang cai dat cac thu vien can thiet tu requirements.txt...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        color 0C
        echo [LOI] Cai dat thu vien that bai! Vui long kiem tra ket noi mang.
        pause
        exit /b 1
    )
)

:: 5. Khoi dong Game
echo.
echo ========================================================
echo [*] Khoi dong game thanh cong! Chuc ban choi game vui ve!
echo ========================================================
echo.
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [THONG BAO] Game da dong hoac gap su co ngoai y muon.
    pause
)
