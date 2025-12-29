@echo off
chcp 65001 >nul
title Okul Zil Programı - EXE Derleme

echo ========================================
echo    OKUL ZİL PROGRAMI - EXE DERLEME
echo ========================================
echo.

REM Çalışma dizinini ayarla
cd /d "%~dp0"

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo Lütfen Python 3.10 veya üzeri sürümünü yükleyin.
    echo.
    pause
    exit /b 1
)

echo Python kontrol edildi...
echo.

REM pathlib paketini kaldır (PyInstaller ile uyumsuz)
echo pathlib paketi kontrol ediliyor...
python -c "import pathlib; import sys; print(sys.path)" >nul 2>&1
python -m pip uninstall pathlib -y >nul 2>&1

REM PyInstaller'ı kontrol et ve yükle
echo PyInstaller kontrol ediliyor...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller bulunamadı. Yükleniyor...
    pip install pyinstaller
    if errorlevel 1 (
        echo [HATA] PyInstaller yüklenemedi!
        pause
        exit /b 1
    )
)

echo.
echo Eski build dosyaları temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OkulZil.spec del /q OkulZil.spec

echo.
echo ========================================
echo EXE derleniyor...
echo ========================================
echo.

REM PyInstaller ile derleme (spec dosyası yoksa oluştur)
if not exist OkulZil.spec (
    echo Spec dosyası bulunamadı, oluşturuluyor...
    pyinstaller --onefile --windowed --name "OkulZil" --add-data "data;data" --add-data "sounds;sounds" main.py
) else (
    pyinstaller OkulZil.spec
)

if errorlevel 1 (
    echo.
    echo [HATA] Derleme başarısız oldu!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Derleme tamamlandı!
echo ========================================
echo.
echo EXE dosyası: dist\OkulZil.exe
echo.
echo Setup dosyası oluşturmak için: build_setup.bat
echo.
pause

