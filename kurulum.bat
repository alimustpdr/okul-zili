@echo off
chcp 65001 >nul
title Okul Zil Programı - Kurulum

echo ========================================
echo    OKUL ZİL PROGRAMI - KURULUM
echo ========================================
echo.

REM Çalışma dizinini ayarla
cd /d "%~dp0"

REM Python kontrolü
echo Python kontrol ediliyor...
python --version
if errorlevel 1 (
    echo.
    echo [HATA] Python bulunamadı!
    echo.
    echo Lütfen Python 3.10 veya üzeri sürümünü yükleyin:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Python bulundu!
echo.

REM pip kontrolü
echo pip kontrol ediliyor...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] pip bulunamadı!
    pause
    exit /b 1
)

echo pip bulundu!
echo.

REM Bağımlılıkları yükle
echo ========================================
echo Bağımlılıklar yükleniyor...
echo ========================================
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [HATA] Bağımlılıklar yüklenemedi!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Kurulum tamamlandı!
echo ========================================
echo.
echo Programı çalıştırmak için 'calistir.bat' dosyasını çalıştırın.
echo.
pause



