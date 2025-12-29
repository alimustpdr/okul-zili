@echo off
chcp 65001 >nul
title Okul Zil Programı - Setup Oluşturma

echo ========================================
echo    OKUL ZİL PROGRAMI - SETUP OLUŞTURMA
echo ========================================
echo.

REM Çalışma dizinini ayarla
cd /d "%~dp0"

REM Önce EXE'nin derlenmiş olması gerekiyor
if not exist "dist\OkulZil.exe" (
    echo [HATA] Önce EXE dosyasını derlemelisiniz!
    echo build_exe.bat dosyasını çalıştırın.
    echo.
    pause
    exit /b 1
)

echo EXE dosyası bulundu: dist\OkulZil.exe
echo.

REM Setup klasörünü oluştur
if not exist "setup" mkdir setup
if exist "setup\*" (
    echo Setup klasörü temizleniyor...
    del /q setup\*.*
    for /d %%d in (setup\*) do rmdir /s /q "%%d"
)

echo.
echo Setup dosyaları hazırlanıyor...
echo.

REM EXE'yi kopyala
copy "dist\OkulZil.exe" "setup\OkulZil.exe" >nul

REM Data klasörünü kopyala
xcopy /E /I /Y "data" "setup\data" >nul

REM Sounds klasörünü kopyala
xcopy /E /I /Y "sounds" "setup\sounds" >nul

REM Logs klasörünü oluştur (boş)
if not exist "setup\logs" mkdir setup\logs

REM README ve diğer dosyaları kopyala
if exist "README.md" copy "README.md" "setup\" >nul

echo.
echo ========================================
echo Setup dosyaları hazırlandı!
echo ========================================
echo.
echo Setup klasörü: setup\
echo.
echo Bu klasörü ZIP olarak paketleyebilir veya
echo Inno Setup ile installer oluşturabilirsiniz.
echo.
echo Inno Setup script: setup\OkulZil_Setup.iss
echo.
pause


