# GitHub'a Yükleme Rehberi

## Adım 1: GitHub'da Repository Oluşturun

1. https://github.com/new adresine gidin
2. Repository adı girin (örn: `okul-zil-programi`)
3. Public veya Private seçin
4. **"Initialize this repository with a README" seçeneğini işaretlemeyin**
5. "Create repository" butonuna tıklayın

## Adım 2: Remote Ekleme ve Push

GitHub'da repository oluşturduktan sonra, size verilen URL'yi kullanın:

```bash
cd okul_zil

# Remote ekleyin (URL'yi kendi repository URL'nizle değiştirin)
git remote add origin https://github.com/KULLANICI_ADI/REPO_ADI.git

# Veya SSH kullanıyorsanız:
# git remote add origin git@github.com:KULLANICI_ADI/REPO_ADI.git

# Dosyaları GitHub'a yükleyin
git push -u origin main
```

## Adım 3: GitHub Kimlik Doğrulama

Eğer GitHub kimlik doğrulama sorunu yaşarsanız:

### Personal Access Token Kullanımı:
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. "Generate new token" → "repo" yetkilerini seçin
3. Token'ı kopyalayın
4. Push yaparken şifre yerine bu token'ı kullanın

### GitHub CLI Kullanımı:
```bash
# GitHub CLI yükleyin (https://cli.github.com/)
gh auth login
git push -u origin main
```

## Hızlı Komutlar

```bash
# Repository durumunu kontrol et
git status

# Değişiklikleri ekle
git add .

# Commit yap
git commit -m "Değişiklik açıklaması"

# GitHub'a gönder
git push origin main
```

## Notlar

- İlk push'tan sonra GitHub'da tüm dosyalarınız görünecektir
- `.gitignore` dosyası gereksiz dosyaları (build, dist, logs vb.) hariç tutar
- Ses dosyaları repository'ye dahil edilmiştir (opsiyonel olarak .gitignore'a eklenebilir)

