# Okul Zil Programı

Windows 10+ için profesyonel, internet gerektirmeyen okul zil sistemi. MEB okullarında sorunsuz kullanım için tasarlanmıştır.

## Özellikler

- ✅ **Otomatik Zil Sistemi**: Haftalık ders programına göre otomatik zil çalma
- ✅ **Manuel Kontroller**: Öğrenci/Öğretmen zili, İstiklal Marşı, Siren vb.
- ✅ **Mod Yönetimi**: Normal, Tatil, Sınav modları
- ✅ **Ses Seviyesi Kontrolü**: Her zil tipi için ayrı ses seviyesi
- ✅ **Sistem Tepsi Desteği**: Arka planda çalışabilir
- ✅ **Log Sistemi**: Tüm olaylar loglanır
- ✅ **İnternet Gerektirmez**: Tamamen offline çalışır
- ✅ **Admin Yetkisi Gerektirmez**: Registry yazmaz, antivirüs dostu

## Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- Windows 10 veya üzeri

### Hızlı Başlangıç (Önerilen)

1. **Kurulum Dosyasını Çalıştırın**
   
   `kurulum.bat` dosyasına çift tıklayın. Bu dosya:
   - Python'un yüklü olup olmadığını kontrol eder
   - Gerekli bağımlılıkları (PySide6) yükler

2. **Programı Çalıştırın**
   
   `calistir.bat` dosyasına çift tıklayın. Program başlar!

### Manuel Kurulum

1. **Projeyi İndirin**
   ```bash
   cd okul_zil
   ```

2. **Bağımlılıkları Yükleyin**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ses Dosyalarını Ekleyin**
   
   Aşağıdaki klasörlere ses dosyalarınızı ekleyin:
   - `sounds/ziller/` - Zil sesleri (örn: zil1.mp3)
   - `sounds/marslar/` - İstiklal Marşı (istiklal.mp3)
   - `sounds/siren/` - Siren sesi (siren.mp3)
   - `sounds/muzik_yayini/` - Teneffüs müzikleri (isteğe bağlı)

4. **Programı Çalıştırın**
   
   **Seçenek 1:** `calistir.bat` dosyasına çift tıklayın (önerilen)
   
   **Seçenek 2:** Konsol modu için `calistir_konsol.bat` (hata mesajlarını görmek için)
   
   **Seçenek 3:** Komut satırından:
   ```bash
   python main.py
   ```

### .BAT Dosyaları

- **`kurulum.bat`**: İlk kurulum için - Python ve bağımlılıkları kontrol eder/yükler
- **`calistir.bat`**: Programı çalıştırır (normal mod)
- **`calistir_konsol.bat`**: Programı çalıştırır (konsol çıktısı görünür, hata ayıklama için)

## Kullanım

### İlk Çalıştırma

Program ilk çalıştırıldığında otomatik olarak:
- `data/schedule.json` - Varsayılan ders programı
- `data/settings.json` - Varsayılan ayarlar

dosyalarını oluşturur.

### Ana Ekran

- **Büyük Saat**: Gerçek zamanlı saat gösterimi
- **Tarih ve Gün**: Mevcut tarih ve haftanın günü
- **Zil Durumu**: AÇIK/KAPALI durumu
- **Aktif Mod**: Normal/Tatil/Sınav modu
- **Geri Sayım**: Sonraki zil için kalan süre

### Manuel Butonlar

- **Öğrenci Zili**: Öğrenci giriş zilini manuel çalar
- **Öğretmen Zili**: Öğretmen giriş zilini manuel çalar
- **Çıkış Zili**: Ders çıkış zilini manuel çalar
- **İstiklal Marşı**: İstiklal Marşı'nı çalar
- **Saygı Duruşu + Marş**: Saygı duruşu ve marş
- **Siren**: Siren sesi
- **DURDUR**: Tüm sesleri durdurur

### Ayarlar

**Ayarlar** butonuna tıklayarak:

- **Ses Seviyeleri**: Her zil tipi için ses seviyesi ayarı (0-100%)
- **Sistem Ayarları**:
  - Windows açılışında başlat
  - Sistem tepsisine küçült
- **Güvenlik**: Şifre koruması (SHA256 hash)
- **Mod**: Normal/Tatil/Sınav modu seçimi

### Ders Programı Düzenleme

`data/schedule.json` dosyasını düzenleyerek ders programınızı özelleştirebilirsiniz.

**Örnek Yapı:**
```json
{
  "days": {
    "Pazartesi": {
      "active": true,
      "lessons": [
        {
          "lesson": 1,
          "ogrenci_giris": "08:30",
          "ogretmen_giris": "08:25",
          "ders_cikis": "09:10",
          "sound": "ziller/zil1.mp3"
        }
      ]
    }
  }
}
```

## .EXE Derleme ve Setup Oluşturma

Detaylı rehber için: **[DERLEME_REHBERI.md](DERLEME_REHBERI.md)**

### Hızlı Başlangıç

1. **EXE Dosyasını Derleyin**
   
   `build_exe.bat` dosyasına çift tıklayın. Script otomatik olarak:
   - Python ve PyInstaller'ı kontrol eder/yükler
   - EXE dosyasını derler
   - Çıktı: `dist\OkulZil.exe`

2. **Setup Dosyalarını Hazırlayın**
   
   `build_setup.bat` dosyasına çift tıklayın. Script otomatik olarak:
   - EXE ve gerekli klasörleri `setup\` klasörüne kopyalar
   - Kurulum için hazır hale getirir

3. **Installer Oluşturun**
   
   **Seçenek A - ZIP (Basit):**
   - `setup` klasörünü ZIP olarak sıkıştırın
   - Kullanıcılara gönderin
   
   **Seçenek B - Inno Setup (Profesyonel):**
   - [Inno Setup](https://jrsoftware.org/isdl.php) indirin (ücretsiz)
   - `setup\OkulZil_Setup.iss` dosyasını açın
   - Build → Compile (F9)
   - Installer: `setup\installer\OkulZil_Setup.exe`

### Manuel Derleme

```bash
# PyInstaller yükle
pip install pyinstaller

# Derle
cd okul_zil
pyinstaller OkulZil.spec

# Çıktı: dist\OkulZil.exe
```

## Klasör Yapısı

```
okul_zil/
│
├─ main.py                 # Ana giriş noktası
├─ requirements.txt        # Python bağımlılıkları
├─ README.md              # Bu dosya
│
├─ core/                  # İş mantığı
│   ├─ scheduler.py       # Zamanlama motoru
│   ├─ sound_player.py    # Ses oynatıcı
│   ├─ state_manager.py   # Durum yöneticisi
│   └─ logger.py          # Log sistemi
│
├─ ui/                    # Kullanıcı arayüzü
│   ├─ main_window.py    # Ana pencere
│   ├─ settings_window.py # Ayarlar penceresi
│   └─ tray.py           # Sistem tepsi ikonu
│
├─ data/                  # Veri dosyaları
│   ├─ schedule.json      # Ders programı
│   └─ settings.json      # Ayarlar
│
├─ sounds/                # Ses dosyaları
│   ├─ ziller/
│   ├─ marslar/
│   ├─ siren/
│   └─ muzik_yayini/
│
└─ logs/                  # Log dosyaları
    └─ zil.log
```

## Log Sistemi

Tüm olaylar `logs/zil.log` dosyasına kaydedilir:

- `[OTOMATIK]` - Otomatik zil çalma olayları
- `[MANUEL]` - Manuel zil çalma olayları
- `[SISTEM]` - Sistem olayları (açılma, kapanma, ayar değişiklikleri)
- `[HATA]` - Hata mesajları
- `[UYARI]` - Uyarı mesajları

## Sorun Giderme

### Ses Çalmıyor

1. Ses dosyalarının doğru klasörde olduğundan emin olun
2. Ses seviyesinin 0'dan büyük olduğunu kontrol edin
3. Windows ses ayarlarını kontrol edin

### Zil Çalmıyor

1. Zil durumunun AÇIK olduğunu kontrol edin
2. Modun Tatil olmadığını kontrol edin
3. `data/schedule.json` dosyasını kontrol edin
4. `logs/zil.log` dosyasına bakın

### Program Açılmıyor

1. Python 3.10+ yüklü olduğundan emin olun
2. `pip install -r requirements.txt` komutunu çalıştırın
3. Hata mesajlarını kontrol edin

## Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

## Destek

Sorularınız için log dosyasını (`logs/zil.log`) kontrol edin ve hata mesajlarını inceleyin.

---

**Not**: Bu program MEB okullarında kullanım için tasarlanmıştır. İnternet bağlantısı gerektirmez ve admin yetkisi gerektirmez.

