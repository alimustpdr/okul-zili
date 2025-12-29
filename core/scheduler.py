"""
Zamanlama motoru - Zil saatlerini kontrol eder ve çalar
"""
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtCore import QTimer, QObject, Signal


class Scheduler(QObject):
    """Zil zamanlama motoru"""
    
    zil_calindi = Signal(str, str, str, str)  # (tip, açıklama, ses_dosyasi, anons_dosyasi) - anons_dosyasi opsiyonel
    
    def __init__(self, schedule_file: str = "data/schedule.json"):
        super().__init__()
        # Çalışma dizinini bul (main.py'nin olduğu yer)
        base_dir = Path(__file__).parent.parent
        self.schedule_file = base_dir / schedule_file
        self.schedule_data: Dict = {}
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_schedule)
        self.timer.setInterval(1000)  # Her 1 saniyede kontrol
        
        # Bugün çalınan zilleri takip et (aynı zil 2 kez çalmasın)
        self._bugun_calan_ziller: set = set()
        self._son_kontrol_tarihi: Optional[datetime] = None
        
        self._load_schedule()
    
    def _load_schedule(self):
        """Zaman çizelgesini yükle"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    self.schedule_data = json.load(f)
            else:
                self.schedule_data = self._default_schedule()
                self._save_schedule()
        except Exception as e:
            print(f"Zaman çizelgesi yüklenirken hata: {e}")
            self.schedule_data = self._default_schedule()
    
    def _save_schedule(self):
        """Zaman çizelgesini kaydet"""
        try:
            self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Zaman çizelgesi kaydedilirken hata: {e}")
    
    def _default_schedule(self) -> Dict:
        """Varsayılan zaman çizelgesi"""
        return {
            "days": {
                "Pazartesi": {
                    "active": True,
                    "lessons": [
                        {
                            "lesson": 1,
                            "ogrenci_giris": "08:30",
                            "ogretmen_giris": "08:25",
                            "ders_cikis": "09:10",
                            "sound": "ziller/zil1.mp3"
                        },
                        {
                            "lesson": 2,
                            "ogrenci_giris": "09:20",
                            "ogretmen_giris": "09:15",
                            "ders_cikis": "10:00",
                            "sound": "ziller/zil1.mp3"
                        },
                        {
                            "lesson": 3,
                            "ogrenci_giris": "10:20",
                            "ogretmen_giris": "10:15",
                            "ders_cikis": "11:00",
                            "sound": "ziller/zil1.mp3"
                        },
                        {
                            "lesson": 4,
                            "ogrenci_giris": "11:20",
                            "ogretmen_giris": "11:15",
                            "ders_cikis": "12:00",
                            "sound": "ziller/zil1.mp3"
                        },
                        {
                            "lesson": 5,
                            "ogrenci_giris": "13:00",
                            "ogretmen_giris": "12:55",
                            "ders_cikis": "13:40",
                            "sound": "ziller/zil1.mp3"
                        },
                        {
                            "lesson": 6,
                            "ogrenci_giris": "13:50",
                            "ogretmen_giris": "13:45",
                            "ders_cikis": "14:30",
                            "sound": "ziller/zil1.mp3"
                        }
                    ]
                },
                "Salı": {"active": True, "lessons": []},
                "Çarşamba": {"active": True, "lessons": []},
                "Perşembe": {"active": True, "lessons": []},
                "Cuma": {"active": True, "lessons": []},
                "Cumartesi": {"active": False, "lessons": []},
                "Pazar": {"active": False, "lessons": []}
            },
            "special_scenarios": {}
        }
    
    def start(self):
        """Zamanlayıcıyı başlat"""
        self.timer.start()
        self._check_schedule()  # İlk kontrolü hemen yap
    
    def stop(self):
        """Zamanlayıcıyı durdur"""
        self.timer.stop()
    
    def _check_schedule(self):
        """Zaman çizelgesini kontrol et"""
        simdi = datetime.now()
        gun_adi = self._get_day_name(simdi.weekday())
        simdiki_saat = simdi.time()
        
        # Gün değiştiyse çalınan zilleri temizle
        if self._son_kontrol_tarihi is None or self._son_kontrol_tarihi.date() != simdi.date():
            self._bugun_calan_ziller.clear()
            self._son_kontrol_tarihi = simdi
        
        # Bugünün derslerini kontrol et
        if gun_adi not in self.schedule_data.get("days", {}):
            return
        
        gun_ayarlari = self.schedule_data["days"][gun_adi]
        
        if not gun_ayarlari.get("active", False):
            return
        
        # Sabahçı-öğlenci sistemi kontrolü
        lessons_to_check = []
        
        # Eğer sabahci ve oglenci alanları varsa, shift sistemi aktif
        if "sabahci" in gun_ayarlari and "oglenci" in gun_ayarlari:
            # Saate göre aktif shift'i belirle (varsayılan: 12:00'den önce sabahçı)
            shift_ayirma_saati = gun_ayarlari.get("shift_ayirma_saati", "12:00")
            try:
                ayirma_saat, ayirma_dakika = map(int, shift_ayirma_saati.split(":"))
                ayirma_zamani = time(ayirma_saat, ayirma_dakika)
                
                if simdiki_saat < ayirma_zamani:
                    # Sabahçı shift'i aktif
                    if gun_ayarlari["sabahci"].get("active", False):
                        lessons_to_check = gun_ayarlari["sabahci"].get("lessons", [])
                else:
                    # Öğlenci shift'i aktif
                    if gun_ayarlari["oglenci"].get("active", False):
                        lessons_to_check = gun_ayarlari["oglenci"].get("lessons", [])
            except:
                # Hata durumunda normal lessons kullan
                lessons_to_check = gun_ayarlari.get("lessons", [])
        else:
            # Normal mod - lessons kullan
            lessons_to_check = gun_ayarlari.get("lessons", [])
        
        # Her ders için kontrol et
        for ders in lessons_to_check:
            # Öğrenci giriş
            if "ogrenci_giris" in ders:
                zil_anahtari = f"{simdi.date()}_{ders['lesson']}_ogrenci_giris"
                if self._zaman_eslesiyor_mu(simdiki_saat, ders["ogrenci_giris"]) and zil_anahtari not in self._bugun_calan_ziller:
                    self._bugun_calan_ziller.add(zil_anahtari)
                    # Öncelik sırası: Ayarlardan seçilen ses > Ders özel sesi > Ders genel sesi > Varsayılan
                    settings_sound = self._get_default_sound("ogrenci")
                    if settings_sound and settings_sound.strip():
                        ses_dosyasi = settings_sound
                    elif ders.get("ogrenci_sound"):
                        ses_dosyasi = ders.get("ogrenci_sound")
                    elif ders.get("sound"):
                        ses_dosyasi = ders.get("sound")
                    else:
                        ses_dosyasi = "ziller/zil1.mp3"
                    anons_dosyasi = ders.get("ogrenci_anons", "")
                    self.zil_calindi.emit("ogrenci_giris", f"{ders['lesson']}. Ders Öğrenci Giriş", ses_dosyasi, anons_dosyasi)
                    return
            
            # Öğretmen giriş
            if "ogretmen_giris" in ders:
                zil_anahtari = f"{simdi.date()}_{ders['lesson']}_ogretmen_giris"
                if self._zaman_eslesiyor_mu(simdiki_saat, ders["ogretmen_giris"]) and zil_anahtari not in self._bugun_calan_ziller:
                    self._bugun_calan_ziller.add(zil_anahtari)
                    # Öncelik sırası: Ayarlardan seçilen ses > Ders özel sesi > Ders genel sesi > Varsayılan
                    settings_sound = self._get_default_sound("ogretmen")
                    if settings_sound and settings_sound.strip():
                        ses_dosyasi = settings_sound
                    elif ders.get("ogretmen_sound"):
                        ses_dosyasi = ders.get("ogretmen_sound")
                    elif ders.get("sound"):
                        ses_dosyasi = ders.get("sound")
                    else:
                        ses_dosyasi = "ziller/zil1.mp3"
                    anons_dosyasi = ders.get("ogretmen_anons", "")
                    self.zil_calindi.emit("ogretmen_giris", f"{ders['lesson']}. Ders Öğretmen Giriş", ses_dosyasi, anons_dosyasi)
                    return
            
            # Ders çıkış
            if "ders_cikis" in ders:
                zil_anahtari = f"{simdi.date()}_{ders['lesson']}_ders_cikis"
                if self._zaman_eslesiyor_mu(simdiki_saat, ders["ders_cikis"]) and zil_anahtari not in self._bugun_calan_ziller:
                    self._bugun_calan_ziller.add(zil_anahtari)
                    # Öncelik sırası: Ayarlardan seçilen ses > Ders özel sesi > Ders genel sesi > Varsayılan
                    settings_sound = self._get_default_sound("cikis")
                    if settings_sound and settings_sound.strip():
                        ses_dosyasi = settings_sound
                    elif ders.get("cikis_sound"):
                        ses_dosyasi = ders.get("cikis_sound")
                    elif ders.get("sound"):
                        ses_dosyasi = ders.get("sound")
                    else:
                        ses_dosyasi = "ziller/zil1.mp3"
                    anons_dosyasi = ders.get("cikis_anons", "")
                    self.zil_calindi.emit("ders_cikis", f"{ders['lesson']}. Ders Çıkış", ses_dosyasi, anons_dosyasi)
                    return
    
    def _zaman_eslesiyor_mu(self, simdiki_saat: time, hedef_saat_str: str) -> bool:
        """Şu anki saat hedef saatle eşleşiyor mu? (saniye hassasiyeti yok)"""
        try:
            saat, dakika = map(int, hedef_saat_str.split(":"))
            hedef_saat = time(saat, dakika)
            
            # Aynı saat ve dakikada mıyız?
            return simdiki_saat.hour == hedef_saat.hour and simdiki_saat.minute == hedef_saat.minute
        except:
            return False
    
    def _get_day_name(self, weekday: int) -> str:
        """Haftanın günü adını döndür (0=Pazartesi)"""
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        return gunler[weekday]
    
    def _get_default_sound(self, tip: str) -> str:
        """Settings'ten varsayılan zil sesini al (boş string döndürebilir)"""
        try:
            base_dir = Path(__file__).parent.parent
            settings_file = base_dir / "data" / "settings.json"
            if settings_file.exists():
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    sounds = settings.get("sounds", {})
                    sound = sounds.get(tip, "")
                    # Eğer ses varsa ve boş değilse döndür
                    if sound and sound.strip():
                        return sound
        except:
            pass
        return ""  # Boş string döndür, böylece ders seslerine bakılabilir
    
    def get_next_zil(self) -> Optional[Dict]:
        """Bir sonraki zil saatini döndür"""
        simdi = datetime.now()
        gun_adi = self._get_day_name(simdi.weekday())
        
        if gun_adi not in self.schedule_data.get("days", {}):
            return None
        
        gun_ayarlari = self.schedule_data["days"][gun_adi]
        
        if not gun_ayarlari.get("active", False):
            return None
        
        # Sabahçı-öğlenci sistemi kontrolü
        lessons_to_check = []
        
        # Eğer sabahci ve oglenci alanları varsa, shift sistemi aktif
        if "sabahci" in gun_ayarlari and "oglenci" in gun_ayarlari:
            # Saate göre aktif shift'i belirle
            shift_ayirma_saati = gun_ayarlari.get("shift_ayirma_saati", "12:00")
            try:
                ayirma_saat, ayirma_dakika = map(int, shift_ayirma_saati.split(":"))
                ayirma_zamani = time(ayirma_saat, ayirma_dakika)
                
                if simdi.time() < ayirma_zamani:
                    # Sabahçı shift'i aktif
                    if gun_ayarlari["sabahci"].get("active", False):
                        lessons_to_check = gun_ayarlari["sabahci"].get("lessons", [])
                else:
                    # Öğlenci shift'i aktif
                    if gun_ayarlari["oglenci"].get("active", False):
                        lessons_to_check = gun_ayarlari["oglenci"].get("lessons", [])
                
                # Gelecek ziller için her iki shift'i de kontrol et
                sabahci_lessons = gun_ayarlari["sabahci"].get("lessons", []) if gun_ayarlari["sabahci"].get("active", False) else []
                oglenci_lessons = gun_ayarlari["oglenci"].get("lessons", []) if gun_ayarlari["oglenci"].get("active", False) else []
                all_lessons = sabahci_lessons + oglenci_lessons
            except:
                all_lessons = gun_ayarlari.get("lessons", [])
        else:
            # Normal mod
            all_lessons = gun_ayarlari.get("lessons", [])
        
        en_yakin_zil = None
        en_yakin_fark = None
        
        for ders in all_lessons:
            for zil_tipi in ["ogrenci_giris", "ogretmen_giris", "ders_cikis"]:
                if zil_tipi in ders:
                    saat_str = ders[zil_tipi]
                    saat, dakika = map(int, saat_str.split(":"))
                    zil_zamani = datetime.combine(simdi.date(), time(saat, dakika))
                    
                    # Geçmiş zamansa yarın olarak hesapla
                    if zil_zamani < simdi:
                        zil_zamani = datetime.combine(
                            (simdi.date() + timedelta(days=1)),
                            time(saat, dakika)
                        )
                    
                    fark = (zil_zamani - simdi).total_seconds()
                    
                    if en_yakin_fark is None or fark < en_yakin_fark:
                        en_yakin_fark = fark
                        en_yakin_zil = {
                            "time": zil_zamani,
                            "type": zil_tipi,
                            "lesson": ders.get("lesson", 0),
                            "sound": ders.get("sound", "ziller/zil1.mp3")
                        }
        
        return en_yakin_zil

