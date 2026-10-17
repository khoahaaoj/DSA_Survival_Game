@echo off
title Dong goi Game sang Windows EXE (PyInstaller)
color 0B
chcp 65001 > nul

echo ========================================================
echo   📦  DONG GOI DSA SURVIVAL GAME THANH WINDOWS EXE
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [LOI] Khong tim thay Python!
    pause
    exit /b 1
)

if exist "venv" (
    call venv\Scripts\activate.bat
)

echo [*] Cai dat / Cap nhat PyInstaller va Pygame...
pip install pyinstaller pygame

echo.
echo [*] Dang tien hanh dong goi voi PyInstaller...
python -m PyInstaller --noconfirm --onedir --windowed ^
    --name "DSA_Survival_Game" ^
    --add-data "assets;assets" ^
    --add-data "settings.py;." ^
    --hidden-import pygame ^
    --collect-all pygame ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo [THÀNH CÔNG] Game da duoc dong goi thanh cong!
    echo Thu muc ket qua nam tai: dist\DSA_Survival_Game\
    echo Ban chi can mo file DSA_Survival_Game.exe de choi!
    echo ========================================================
) else (
    color 0C
    echo.
    echo [THAT BAI] Qua trinh build gap loi!
)
pause
