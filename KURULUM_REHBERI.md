# Okul Zil Programı - Kurulum Rehberi (Kullanıcılar İçin)

Bu rehber, Okul Zil Programını bilgisayarınıza kurmak için adım adım talimatlar içerir.

## 📥 Kurulum Yöntemleri

### Yöntem 1: Setup Installer (Önerilen)

1. **Setup Dosyasını İndirin**
   - `OkulZil_Setup.exe` dosyasını indirin

2. **Setup'ı Çalıştırın**
   - Dosyaya çift tıklayın
   - Windows güvenlik uyarısı çıkarsa "Daha fazla bilgi" → "Yine de çalıştır" seçin
   - (Program admin yetkisi gerektirmez, güvenlidir)

3. **Kurulum Sihirbazını Takip Edin**
   - Kurulum klasörünü seçin (varsayılan: `C:\Program Files\Okul Zil Programı`)
   - Masaüstü kısayolu oluşturmak isteyip istemediğinizi seçin
   - Windows başlangıcında otomatik başlatma seçeneğini işaretleyin (isteğe bağlı)

4. **Kurulumu Tamamlayın**
   - "Kur" butonuna tıklayın
   - Kurulum tamamlandığında program otomatik açılır

### Yöntem 2: ZIP Dosyası (Portable)

1. **ZIP Dosyasını İndirin ve Açın**
   - `OkulZil.zip` dosyasını indirin
   - ZIP'i bir klasöre çıkartın (örn: `C:\OkulZil`)

2. **Programı Çalıştırın**
   - `OkulZil.exe` dosyasına çift tıklayın
   - İlk çalıştırmada kurulum sihirbazı açılır

## 🎯 İlk Kullanım

Program ilk açıldığında **Kurulum Sihirbazı** otomatik başlar:

1. **Ders Süresi**: Standart ders süresini girin (örn: 40 dakika)
2. **Teneffüs Süresi**: Standart teneffüs süresini girin (örn: 10 dakika)
3. **İlk Ders Saati**: İlk dersin başlangıç saatini girin (örn: 08:30)
4. **Günlük Ders Sayısı**: Günlük kaç ders olduğunu girin (örn: 8)
5. **Öğle Arası**: Öğle arası bilgilerini girin
6. **Öğrenci/Öğretmen Zili**: Zil ayarlarını yapın

Sihirbazı tamamladıktan sonra program hazırdır!

## 📁 Kurulum Sonrası Klasör Yapısı

Program kurulduktan sonra şu klasör yapısı oluşur:

```
Okul Zil Programı/
├─ OkulZil.exe          # Ana program
├─ data/                # Ayarlar ve program verileri
│   ├─ schedule.json    # Ders programı
│   └─ settings.json    # Program ayarları
├─ sounds/              # Ses dosyaları
│   ├─ ziller/         # Zil sesleri
│   ├─ marslar/        # İstiklal Marşı
│   └─ siren/          # Siren sesleri
└─ logs/                # Log dosyaları
    └─ zil.log         # Program logları
```

## ⚙️ Ayarlar

### Ses Dosyalarını Değiştirme

1. Programı açın
2. "Ayarlar" butonuna tıklayın
3. "Ses Seçimi" bölümünden istediğiniz ses dosyasını seçin
4. Ses dosyalarını `sounds` klasörüne kopyalayabilirsiniz

### Ders Programını Düzenleme

1. Ana ekranda "Ders Programı" butonuna tıklayın
2. İstediğiniz günü seçin
3. Ders saatlerini düzenleyin
4. "Kaydet" butonuna tıklayın

### Windows Başlangıcında Otomatik Başlatma

**Yöntem 1: Program İçinden**
1. Ayarlar → "Windows açılışında başlat" seçeneğini işaretleyin

**Yöntem 2: Manuel**
1. Windows tuşu + R
2. `shell:startup` yazın ve Enter
3. `OkulZil.exe` için kısayol oluşturun

## 🔧 Sorun Giderme

### Program Açılmıyor

1. **Antivirüs Kontrolü**
   - Bazı antivirüsler .exe dosyalarını engelleyebilir
   - Programı antivirüs istisnalarına ekleyin

2. **Windows Defender**
   - Windows Defender → Virüs ve tehdit koruması
   - Programı istisnalara ekleyin

3. **Log Dosyasını Kontrol Edin**
   - `logs\zil.log` dosyasını açın
   - Hata mesajlarını kontrol edin

### Ses Çalmıyor

1. **Ses Dosyalarını Kontrol Edin**
   - `sounds` klasöründe ses dosyalarının olduğundan emin olun
   - Dosya formatlarının desteklendiğinden emin olun (MP3, WAV, OGG, M4A, AAC, FLAC, WMA)

2. **Ses Seviyesini Kontrol Edin**
   - Ayarlar → Ses Seviyeleri
   - Her zil tipi için ses seviyesinin 0'dan büyük olduğundan emin olun

3. **Windows Ses Ayarları**
   - Windows ses ayarlarını kontrol edin
   - Ses çıkış cihazının doğru seçildiğinden emin olun

### Zil Çalmıyor

1. **Zil Durumunu Kontrol Edin**
   - Ana ekranda "Zil: AÇIK" yazısını kontrol edin
   - Kapalıysa "Zili Aç" butonuna tıklayın

2. **Mod Kontrolü**
   - Modun "Tatil" olmadığından emin olun
   - Normal modda olmalı

3. **Ders Programını Kontrol Edin**
   - Ders Programı → Bugünün programını kontrol edin
   - Zil saatlerinin doğru olduğundan emin olun

### Sistem Tepsisinde Görünmüyor

1. **Gizli İkonları Göster**
   - Windows görev çubuğunda ok simgesine tıklayın
   - "Gizli simgeleri göster" seçeneğini açın

2. **Programı Yeniden Başlatın**
   - Programı kapatıp yeniden açın
   - Sistem tepsi ikonu görünmelidir

## 📞 Destek

Sorun yaşıyorsanız:

1. **Log Dosyasını Kontrol Edin**
   - `logs\zil.log` dosyasını açın
   - Hata mesajlarını not edin

2. **Program Bilgilerini Toplayın**
   - Windows sürümü
   - Program versiyonu
   - Hata mesajları

3. **Yardım İsteyin**
   - Log dosyasını ve hata mesajlarını paylaşın

## 🔄 Güncelleme

Programı güncellemek için:

1. Eski programı kapatın
2. Yeni setup dosyasını çalıştırın
3. Aynı klasöre kurun (ayarlar korunur)

**Not**: Ayarlarınız ve ders programınız otomatik olarak korunur.

## 🗑️ Kaldırma

### Setup ile Kurulduysa

1. Windows Ayarlar → Uygulamalar
2. "Okul Zil Programı"nı bulun
3. "Kaldır" butonuna tıklayın

### Portable (ZIP) İse

1. Program klasörünü silin
2. Masaüstü kısayolunu silin (varsa)
3. Startup klasöründen kısayolu silin (varsa)

**Not**: Ayarlar ve loglar silinir. Yedeklemek isterseniz `data` klasörünü kopyalayın.

---

**Son Güncelleme:** 2025  
**Versiyon:** 1.0


