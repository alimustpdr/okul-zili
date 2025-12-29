@echo off
chcp 65001 >nul
title Okul Zil Programı (Konsol Modu)

echo ========================================
echo    OKUL ZİL PROGRAMI - KONSOL MODU
echo ========================================
echo.

REM Çalışma dizinini ayarla
cd /d "%~dp0"

REM Python'un yüklü olup olmadığını kontrol et
python --version
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo Lütfen Python 3.10 veya üzeri sürümünü yükleyin.
    echo.
    pause
    exit /b 1
)

echo.
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
echo ========================================
echo.

REM Programı çalıştır (konsol çıktısı görünür)
python main.py

REM Program kapandığında
if errorlevel 1 (
    echo.
    echo [HATA] Program bir hata ile kapandı.
    echo Log dosyasını kontrol edin: logs\zil.log
    echo.
)

pause



