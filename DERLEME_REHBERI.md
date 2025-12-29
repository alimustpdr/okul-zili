# Okul Zil Programı - EXE Derleme ve Setup Rehberi

Bu rehber, Okul Zil Programını Windows için .exe dosyasına derlemek ve kurulum paketi oluşturmak için adım adım talimatlar içerir.

## 📋 Gereksinimler

1. **Python 3.10 veya üzeri** - [python.org](https://www.python.org/downloads/)
2. **PyInstaller** - Otomatik yüklenecek
3. **Inno Setup (Opsiyonel)** - Profesyonel installer için - [jrsoftware.org](https://jrsoftware.org/isdl.php)

## 🚀 Hızlı Başlangıç

### Adım 1: EXE Dosyasını Derle

1. `build_exe.bat` dosyasına çift tıklayın
2. Script otomatik olarak:
   - Python'u kontrol eder
   - PyInstaller'ı yükler (gerekirse)
   - Eski build dosyalarını temizler
   - EXE dosyasını derler

3. Derleme tamamlandığında `dist\OkulZil.exe` dosyası oluşur

### Adım 2: Setup Dosyalarını Hazırla

1. `build_setup.bat` dosyasına çift tıklayın
2. Script otomatik olarak:
   - EXE dosyasını kontrol eder
   - Gerekli klasörleri (data, sounds, logs) kopyalar
   - Setup klasörünü hazırlar

### Adım 3: Installer Oluştur (İki Seçenek)

#### Seçenek A: ZIP Dosyası (Basit)

1. `setup` klasörünü ZIP olarak sıkıştırın
2. Kullanıcılara ZIP dosyasını gönderin
3. Kullanıcılar ZIP'i açıp `OkulZil.exe` dosyasını çalıştırabilir

#### Seçenek B: Inno Setup Installer (Profesyonel)

1. **Inno Setup'ı İndirin ve Yükleyin**
   - [Inno Setup İndir](https://jrsoftware.org/isdl.php)
   - Ücretsiz ve açık kaynak

2. **Inno Setup Compiler'ı Açın**

3. **Script Dosyasını Yükleyin**
   - File → Open
   - `setup\OkulZil_Setup.iss` dosyasını seçin

4. **Derleyin**
   - Build → Compile (F9)
   - Installer dosyası `setup\installer\OkulZil_Setup.exe` olarak oluşur

5. **Test Edin**
   - Oluşan installer'ı çalıştırın
   - Kurulumu test edin

## 📁 Dosya Yapısı

Derleme sonrası oluşan klasör yapısı:

```
okul_zil/
├─ build/              # Geçici build dosyaları (silinebilir)
├─ dist/              # Derlenmiş EXE dosyası
│   └─ OkulZil.exe
├─ setup/             # Setup dosyaları
│   ├─ OkulZil.exe
│   ├─ data/
│   ├─ sounds/
│   ├─ logs/
│   ├─ README.md
│   └─ OkulZil_Setup.iss  # Inno Setup script
└─ installer/         # Inno Setup çıktısı (varsa)
    └─ OkulZil_Setup.exe
```

## 🔧 Manuel Derleme

Eğer batch dosyaları çalışmıyorsa, manuel olarak derleyebilirsiniz:

### 1. PyInstaller'ı Yükleyin

```bash
pip install pyinstaller
```

### 2. Spec Dosyası ile Derleyin

```bash
cd okul_zil
pyinstaller OkulZil.spec
```

### 3. Veya Doğrudan Komut ile Derleyin

```bash
pyinstaller --onefile --windowed --name "OkulZil" --add-data "data;data" --add-data "sounds;sounds" main.py
```

## ⚙️ PyInstaller Ayarları

`OkulZil.spec` dosyası PyInstaller ayarlarını içerir:

- **`--onefile`**: Tek dosya EXE oluşturur
- **`--windowed`**: Konsol penceresi göstermez
- **`datas`**: Data ve sounds klasörlerini dahil eder
- **`hiddenimports`**: PySide6 modüllerini dahil eder

## 🐛 Sorun Giderme

### EXE Derlenemiyor

1. **Python ve PyInstaller Kontrolü**
   ```bash
   python --version
   pip list | findstr PyInstaller
   ```

2. **Bağımlılıkları Yükleyin**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

3. **Eski Dosyaları Temizleyin**
   ```bash
   rmdir /s /q build dist
   del OkulZil.spec
   ```

### EXE Çalışmıyor

1. **Konsol Modunda Test Edin**
   - `OkulZil.spec` dosyasında `console=False` yerine `console=True` yapın
   - Yeniden derleyin
   - Hata mesajlarını kontrol edin

2. **Log Dosyasını Kontrol Edin**
   - Program çalıştığında `logs\zil.log` dosyasını kontrol edin

3. **Dosya Yollarını Kontrol Edin**
   - EXE'nin yanında `data` ve `sounds` klasörlerinin olduğundan emin olun

### Ses Dosyaları Bulunamıyor

1. **Klasör Yapısını Kontrol Edin**
   ```
   OkulZil.exe
   ├─ data/
   ├─ sounds/
   │   ├─ ziller/
   │   ├─ marslar/
   │   └─ siren/
   └─ logs/
   ```

2. **Spec Dosyasında Data Klasörlerini Kontrol Edin**
   - `OkulZil.spec` dosyasında `datas` bölümünü kontrol edin

## 📦 Dağıtım

### Minimum Gereksinimler

Kullanıcıların ihtiyacı olan minimum dosyalar:

```
OkulZil.exe
data/
  ├─ schedule.json
  └─ settings.json
sounds/
  ├─ ziller/
  ├─ marslar/
  └─ siren/
logs/ (boş klasör)
```

### İlk Çalıştırma

Program ilk çalıştırıldığında:
- Kurulum sihirbazı otomatik açılır
- Kullanıcı ayarları yapar
- `data\schedule.json` ve `data\settings.json` otomatik oluşur

## 🔐 Güvenlik Notları

- Program **admin yetkisi gerektirmez**
- **Registry'ye yazmaz**
- **Antivirüs dostu** (kod imzalama yoksa bazı antivirüsler uyarı verebilir)
- Tüm veriler program klasöründe saklanır

## 📝 Lisans ve Notlar

- Program MEB okullarında kullanım için tasarlanmıştır
- İnternet bağlantısı gerektirmez
- Tamamen offline çalışır

## 🆘 Yardım

Sorun yaşıyorsanız:
1. `logs\zil.log` dosyasını kontrol edin
2. Konsol modunda çalıştırıp hata mesajlarını okuyun
3. GitHub Issues'da sorun bildirin (varsa)

---

**Son Güncelleme:** 2025
**Versiyon:** 1.0


