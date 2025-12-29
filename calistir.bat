@echo off
chcp 65001 >nul
title Okul Zil Programı

echo ========================================
echo    OKUL ZİL PROGRAMI
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

REM Bağımlılıkları kontrol et
echo Bağımlılıklar kontrol ediliyor...
python -c "import PySide6" >nul 2>&1
if errorlevel 1 (
    echo PySide6 bulunamadı. Yükleniyor...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [HATA] Bağımlılıklar yüklenemedi!
        pause
        exit /b 1
    )
)

echo.
echo Program başlatılıyor...
echo.

REM Programı çalıştır
python main.py

REM Program kapandığında
if errorlevel 1 (
    echo.
    echo [HATA] Program bir hata ile kapandı.
    echo Log dosyasını kontrol edin: logs\zil.log
    echo.
    pause
)


