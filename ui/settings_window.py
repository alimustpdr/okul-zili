"""
Ayarlar penceresi
"""
import json
import hashlib
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QCheckBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog,
    QScrollArea, QFormLayout, QGroupBox
)
from PySide6.QtCore import Qt
import os


class SettingsWindow(QDialog):
    """Ayarlar penceresi"""
    
    def __init__(self, settings_file: str = "data/settings.json", parent=None):
        super().__init__(parent)
        # Çalışma dizinini bul (main.py'nin olduğu yer)
        base_dir = Path(__file__).parent.parent
        self.settings_file = base_dir / settings_file
        self.settings_data = {}
        self._load_settings()
        
        self.setWindowTitle("Ayarlar")
        
        # Ekran boyutuna göre pencere boyutunu ayarla
        screen = self.screen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Maksimum boyut: ekran boyutunun %90'ı
        max_width = int(screen_width * 0.95)
        max_height = int(screen_height * 0.90)
        
        # Minimum ve başlangıç boyutu
        min_width = 700
        min_height = 600
        start_width = min(max_width, 900)
        start_height = min(max_height, 800)
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        self.resize(start_width, start_height)
        
        # Pencereyi ekranın ortasına yerleştir
        if parent:
            parent_geometry = parent.geometry()
            self.move(
                parent_geometry.x() + (parent_geometry.width() - start_width) // 2,
                parent_geometry.y() + (parent_geometry.height() - start_height) // 2
            )
        else:
            self.move(
                (screen_width - start_width) // 2,
                (screen_height - start_height) // 2
            )
        
        self._setup_ui()
        self._load_ui_from_settings()
    
    def _setup_ui(self):
        """UI'ı oluştur"""
        layout = QVBoxLayout()
        
        # Sekmeler
        tabs = QTabWidget()
        
        # Genel ayarlar - ScrollArea ile
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        genel_tab_content = QWidget()
        genel_layout = QVBoxLayout()
        genel_layout.setSpacing(15)
        genel_layout.setContentsMargins(15, 15, 15, 15)
        
        # Ses seviyeleri grubu
        ses_seviyeleri_group = QGroupBox("Ses Seviyeleri (%)")
        ses_seviyeleri_layout = QFormLayout()
        ses_seviyeleri_layout.setSpacing(10)
        
        self.ogrenci_volume = QSpinBox()
        self.ogrenci_volume.setRange(0, 100)
        self.ogrenci_volume.setValue(100)
        self.ogrenci_volume.setMinimumWidth(100)
        ses_seviyeleri_layout.addRow("Öğrenci Zili:", self.ogrenci_volume)
        
        self.ogretmen_volume = QSpinBox()
        self.ogretmen_volume.setRange(0, 100)
        self.ogretmen_volume.setValue(100)
        self.ogretmen_volume.setMinimumWidth(100)
        ses_seviyeleri_layout.addRow("Öğretmen Zili:", self.ogretmen_volume)
        
        self.cikis_volume = QSpinBox()
        self.cikis_volume.setRange(0, 100)
        self.cikis_volume.setValue(100)
        self.cikis_volume.setMinimumWidth(100)
        ses_seviyeleri_layout.addRow("Çıkış Zili:", self.cikis_volume)
        
        self.mars_volume = QSpinBox()
        self.mars_volume.setRange(0, 100)
        self.mars_volume.setValue(100)
        self.mars_volume.setMinimumWidth(100)
        ses_seviyeleri_layout.addRow("İstiklal Marşı:", self.mars_volume)
        
        self.siren_volume = QSpinBox()
        self.siren_volume.setRange(0, 100)
        self.siren_volume.setValue(100)
        self.siren_volume.setMinimumWidth(100)
        ses_seviyeleri_layout.addRow("Siren:", self.siren_volume)
        
        ses_seviyeleri_group.setLayout(ses_seviyeleri_layout)
        genel_layout.addWidget(ses_seviyeleri_group)
        
        # Sesler grubu - Ana sayfadaki tüm butonlar için
        sesler_group = QGroupBox("Ses Dosyaları")
        sesler_layout = QFormLayout()
        sesler_layout.setSpacing(10)
        
        # Öğrenci Zili
        ogrenci_layout = QHBoxLayout()
        self.ogrenci_sound_label = QLabel("ziller/zil1.mp3")
        self.ogrenci_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.ogrenci_sound_label.setWordWrap(True)
        self.ogrenci_sound_label.setMinimumWidth(400)
        ogrenci_layout.addWidget(self.ogrenci_sound_label)
        ogrenci_btn = QPushButton("Seç...")
        ogrenci_btn.setMinimumWidth(80)
        ogrenci_btn.clicked.connect(lambda: self._select_sound_file("ogrenci", "ziller"))
        ogrenci_layout.addWidget(ogrenci_btn)
        sesler_layout.addRow("Öğrenci Zili:", ogrenci_layout)
        
        # Öğretmen Zili
        ogretmen_layout = QHBoxLayout()
        self.ogretmen_sound_label = QLabel("ziller/zil1.mp3")
        self.ogretmen_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.ogretmen_sound_label.setWordWrap(True)
        self.ogretmen_sound_label.setMinimumWidth(400)
        ogretmen_layout.addWidget(self.ogretmen_sound_label)
        ogretmen_btn = QPushButton("Seç...")
        ogretmen_btn.setMinimumWidth(80)
        ogretmen_btn.clicked.connect(lambda: self._select_sound_file("ogretmen", "ziller"))
        ogretmen_layout.addWidget(ogretmen_btn)
        sesler_layout.addRow("Öğretmen Zili:", ogretmen_layout)
        
        # Çıkış Zili
        cikis_layout = QHBoxLayout()
        self.cikis_sound_label = QLabel("ziller/zil1.mp3")
        self.cikis_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.cikis_sound_label.setWordWrap(True)
        self.cikis_sound_label.setMinimumWidth(400)
        cikis_layout.addWidget(self.cikis_sound_label)
        cikis_btn = QPushButton("Seç...")
        cikis_btn.setMinimumWidth(80)
        cikis_btn.clicked.connect(lambda: self._select_sound_file("cikis", "ziller"))
        cikis_layout.addWidget(cikis_btn)
        sesler_layout.addRow("Çıkış Zili:", cikis_layout)
        
        # İstiklal Marşı
        mars_layout = QHBoxLayout()
        self.mars_sound_label = QLabel("marslar/istiklal.mp3")
        self.mars_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.mars_sound_label.setWordWrap(True)
        self.mars_sound_label.setMinimumWidth(400)
        mars_layout.addWidget(self.mars_sound_label)
        mars_btn = QPushButton("Seç...")
        mars_btn.setMinimumWidth(80)
        mars_btn.clicked.connect(lambda: self._select_sound_file("mars", "marslar"))
        mars_layout.addWidget(mars_btn)
        sesler_layout.addRow("İstiklal Marşı:", mars_layout)
        
        # Siren
        siren_layout = QHBoxLayout()
        self.siren_sound_label = QLabel("siren/siren.mp3")
        self.siren_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.siren_sound_label.setWordWrap(True)
        self.siren_sound_label.setMinimumWidth(400)
        siren_layout.addWidget(self.siren_sound_label)
        siren_btn = QPushButton("Seç...")
        siren_btn.setMinimumWidth(80)
        siren_btn.clicked.connect(lambda: self._select_sound_file("siren", "siren"))
        siren_layout.addWidget(siren_btn)
        sesler_layout.addRow("Siren:", siren_layout)
        
        # Saygı Duruşu
        saygi_layout = QHBoxLayout()
        self.saygi_sound_label = QLabel("")
        self.saygi_sound_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.saygi_sound_label.setWordWrap(True)
        self.saygi_sound_label.setMinimumWidth(400)
        saygi_layout.addWidget(self.saygi_sound_label)
        saygi_btn = QPushButton("Seç...")
        saygi_btn.setMinimumWidth(80)
        saygi_btn.clicked.connect(lambda: self._select_sound_file("saygi", "marslar"))
        saygi_layout.addWidget(saygi_btn)
        sesler_layout.addRow("Saygı Duruşu:", saygi_layout)
        
        # Siren + İstiklal Marşı (Siren)
        siren_mars_siren_layout = QHBoxLayout()
        self.siren_mars_siren_label = QLabel("siren/siren.mp3")
        self.siren_mars_siren_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.siren_mars_siren_label.setWordWrap(True)
        self.siren_mars_siren_label.setMinimumWidth(400)
        siren_mars_siren_layout.addWidget(self.siren_mars_siren_label)
        siren_mars_siren_btn = QPushButton("Seç...")
        siren_mars_siren_btn.setMinimumWidth(80)
        siren_mars_siren_btn.clicked.connect(lambda: self._select_sound_file("siren_mars_siren", "siren"))
        siren_mars_siren_layout.addWidget(siren_mars_siren_btn)
        sesler_layout.addRow("Siren + İstiklal Marşı (Siren):", siren_mars_siren_layout)
        
        # Siren + İstiklal Marşı (Marş)
        siren_mars_mars_layout = QHBoxLayout()
        self.siren_mars_mars_label = QLabel("marslar/istiklal.mp3")
        self.siren_mars_mars_label.setStyleSheet("border: 1px solid gray; padding: 5px; background-color: white; min-height: 20px;")
        self.siren_mars_mars_label.setWordWrap(True)
        self.siren_mars_mars_label.setMinimumWidth(400)
        siren_mars_mars_layout.addWidget(self.siren_mars_mars_label)
        siren_mars_mars_btn = QPushButton("Seç...")
        siren_mars_mars_btn.setMinimumWidth(80)
        siren_mars_mars_btn.clicked.connect(lambda: self._select_sound_file("siren_mars_mars", "marslar"))
        siren_mars_mars_layout.addWidget(siren_mars_mars_btn)
        sesler_layout.addRow("Siren + İstiklal Marşı (Marş):", siren_mars_mars_layout)
        
        sesler_group.setLayout(sesler_layout)
        genel_layout.addWidget(sesler_group)
        
        # Sistem ayarları grubu
        sistem_group = QGroupBox("Sistem Ayarları")
        sistem_layout = QVBoxLayout()
        sistem_layout.setSpacing(10)
        
        self.startup_checkbox = QCheckBox("Windows açılışında başlat")
        sistem_layout.addWidget(self.startup_checkbox)
        
        self.tray_checkbox = QCheckBox("Sistem tepsisine küçült")
        sistem_layout.addWidget(self.tray_checkbox)
        
        sistem_group.setLayout(sistem_layout)
        genel_layout.addWidget(sistem_group)
        
        # Güvenlik grubu
        guvenlik_group = QGroupBox("Güvenlik")
        guvenlik_layout = QFormLayout()
        guvenlik_layout.setSpacing(10)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumWidth(400)
        guvenlik_layout.addRow("Şifre (boş bırakılırsa şifre kaldırılır):", self.password_input)
        
        guvenlik_group.setLayout(guvenlik_layout)
        genel_layout.addWidget(guvenlik_group)
        
        genel_layout.addStretch()
        
        genel_tab_content.setLayout(genel_layout)
        scroll_area.setWidget(genel_tab_content)
        
        genel_tab = QWidget()
        genel_tab_layout = QVBoxLayout()
        genel_tab_layout.setContentsMargins(0, 0, 0, 0)
        genel_tab_layout.addWidget(scroll_area)
        genel_tab.setLayout(genel_tab_layout)
        tabs.addTab(genel_tab, "Genel")
        
        # Mod ayarları
        mod_tab = QWidget()
        mod_layout = QVBoxLayout()
        
        mod_layout.addWidget(QLabel("<b>Zil Modu</b>"))
        
        self.normal_radio = QCheckBox("Normal Mod")
        self.normal_radio.setChecked(True)
        mod_layout.addWidget(self.normal_radio)
        
        self.tatil_radio = QCheckBox("Tatil Modu (Ziller çalışmaz)")
        mod_layout.addWidget(self.tatil_radio)
        
        self.sinav_radio = QCheckBox("Sınav Modu")
        mod_layout.addWidget(self.sinav_radio)
        
        mod_layout.addStretch()
        mod_tab.setLayout(mod_layout)
        tabs.addTab(mod_tab, "Mod")
        
        layout.addWidget(tabs)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        kaydet_btn = QPushButton("Kaydet")
        kaydet_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(kaydet_btn)
        
        iptal_btn = QPushButton("İptal")
        iptal_btn.clicked.connect(self.reject)
        button_layout.addWidget(iptal_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_settings(self):
        """Ayarları yükle"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings_data = json.load(f)
            else:
                self.settings_data = self._default_settings()
                self._save_settings()
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            self.settings_data = self._default_settings()
    
    def _default_settings(self) -> dict:
        """Varsayılan ayarlar"""
        return {
            "volumes": {
                "ogrenci": 100,
                "ogretmen": 100,
                "cikis": 100,
                "mars": 100,
                "siren": 100
            },
            "sounds": {
                "ogrenci": "ziller/zil1.mp3",
                "ogretmen": "ziller/zil1.mp3",
                "cikis": "ziller/zil1.mp3",
                "mars": "marslar/istiklal.mp3",
                "siren": "siren/siren.mp3",
                "saygi": "",
                "siren_mars_siren": "siren/siren.mp3",
                "siren_mars_mars": "marslar/istiklal.mp3"
            },
            "system": {
                "startup": False,
                "tray": True
            },
            "security": {
                "password_hash": None
            },
            "mode": "normal"
        }
    
    def _load_ui_from_settings(self):
        """UI'ı ayarlardan doldur"""
        volumes = self.settings_data.get("volumes", {})
        self.ogrenci_volume.setValue(volumes.get("ogrenci", 100))
        self.ogretmen_volume.setValue(volumes.get("ogretmen", 100))
        self.cikis_volume.setValue(volumes.get("cikis", 100))
        self.mars_volume.setValue(volumes.get("mars", 100))
        self.siren_volume.setValue(volumes.get("siren", 100))
        
        sounds = self.settings_data.get("sounds", {})
        self.ogrenci_sound_label.setText(sounds.get("ogrenci", "ziller/zil1.mp3"))
        self.ogretmen_sound_label.setText(sounds.get("ogretmen", "ziller/zil1.mp3"))
        self.cikis_sound_label.setText(sounds.get("cikis", "ziller/zil1.mp3"))
        self.mars_sound_label.setText(sounds.get("mars", "marslar/istiklal.mp3"))
        self.siren_sound_label.setText(sounds.get("siren", "siren/siren.mp3"))
        saygi = sounds.get("saygi", "")
        self.saygi_sound_label.setText(saygi if saygi else "(Seçilmedi)")
        self.siren_mars_siren_label.setText(sounds.get("siren_mars_siren", "siren/siren.mp3"))
        self.siren_mars_mars_label.setText(sounds.get("siren_mars_mars", "marslar/istiklal.mp3"))
        
        system = self.settings_data.get("system", {})
        self.startup_checkbox.setChecked(system.get("startup", False))
        self.tray_checkbox.setChecked(system.get("tray", True))
        
        mode = self.settings_data.get("mode", "normal")
        self.normal_radio.setChecked(mode == "normal")
        self.tatil_radio.setChecked(mode == "tatil")
        self.sinav_radio.setChecked(mode == "sinav")
    
    def _save_settings(self):
        """Ayarları kaydet"""
        # Ses seviyeleri
        self.settings_data["volumes"] = {
            "ogrenci": self.ogrenci_volume.value(),
            "ogretmen": self.ogretmen_volume.value(),
            "cikis": self.cikis_volume.value(),
            "mars": self.mars_volume.value(),
            "siren": self.siren_volume.value()
        }
        
        # Ses dosyaları
        saygi_text = self.saygi_sound_label.text()
        if saygi_text == "(Seçilmedi)":
            saygi_text = ""
        
        self.settings_data["sounds"] = {
            "ogrenci": self.ogrenci_sound_label.text(),
            "ogretmen": self.ogretmen_sound_label.text(),
            "cikis": self.cikis_sound_label.text(),
            "mars": self.mars_sound_label.text(),
            "siren": self.siren_sound_label.text(),
            "saygi": saygi_text,
            "siren_mars_siren": self.siren_mars_siren_label.text(),
            "siren_mars_mars": self.siren_mars_mars_label.text()
        }
        
        # Sistem ayarları
        self.settings_data["system"] = {
            "startup": self.startup_checkbox.isChecked(),
            "tray": self.tray_checkbox.isChecked()
        }
        
        # Startup ayarını uygula
        old_startup = self.settings_data.get("system", {}).get("startup", False)
        new_startup = self.startup_checkbox.isChecked()
        if old_startup != new_startup:
            self._update_startup(new_startup)
        
        # Şifre
        sifre = self.password_input.text()
        if sifre:
            sifre_hash = hashlib.sha256(sifre.encode()).hexdigest()
            self.settings_data["security"]["password_hash"] = sifre_hash
        else:
            self.settings_data["security"]["password_hash"] = None
        
        # Mod
        if self.normal_radio.isChecked():
            self.settings_data["mode"] = "normal"
        elif self.tatil_radio.isChecked():
            self.settings_data["mode"] = "tatil"
        elif self.sinav_radio.isChecked():
            self.settings_data["mode"] = "sinav"
        
        # Dosyaya kaydet
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Başarılı", "Ayarlar kaydedildi!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Ayarlar kaydedilirken hata oluştu:\n{e}")
    
    def _select_sound_file(self, tip: str, target_subfolder: str = "ziller"):
        """Zil sesi dosyası seç"""
        base_dir = Path(__file__).parent.parent
        sounds_dir = base_dir / "sounds"
        target_dir = sounds_dir / target_subfolder
        
        # Varsayılan klasör - önce hedef klasör, sonra sounds, sonra base
        if target_dir.exists():
            default_path = str(target_dir)
        elif sounds_dir.exists():
            default_path = str(sounds_dir)
        else:
            default_path = str(base_dir)
        
        tip_names = {
            "ogrenci": "Öğrenci Zili",
            "ogretmen": "Öğretmen Zili",
            "cikis": "Çıkış Zili",
            "mars": "İstiklal Marşı",
            "siren": "Siren",
            "saygi": "Saygı Duruşu",
            "siren_mars_siren": "Siren + İstiklal Marşı (Siren)",
            "siren_mars_mars": "Siren + İstiklal Marşı (Marş)"
        }
        
        tip_name = tip_names.get(tip, tip.capitalize())
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"{tip_name} İçin Ses Dosyası Seç",
            default_path,
            "Ses Dosyaları (*.mp3 *.wav *.ogg *.m4a *.aac *.flac *.wma);;MP3 Dosyaları (*.mp3);;WAV Dosyaları (*.wav);;OGG Dosyaları (*.ogg);;Tüm Dosyalar (*.*)"
        )
        
        if file_path:
            # Dosyayı sounds klasörüne kopyala (eğer zaten orada değilse)
            file_path_obj = Path(file_path)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Eğer dosya sounds klasörü dışındaysa kopyala
            if not file_path_obj.is_relative_to(sounds_dir):
                target_file = target_dir / file_path_obj.name
                try:
                    import shutil
                    shutil.copy2(file_path_obj, target_file)
                    relative_path = f"{target_subfolder}/{file_path_obj.name}"
                except Exception as e:
                    QMessageBox.warning(self, "Uyarı", f"Dosya kopyalanamadı: {e}\nMutlak yol kullanılacak.")
                    # Mutlak yol yerine relative path dene
                    try:
                        relative_path = str(file_path_obj.relative_to(base_dir)).replace("\\", "/")
                    except:
                        relative_path = file_path.replace("\\", "/")
            else:
                # Zaten sounds klasöründe, relative path kullan
                relative_path = str(file_path_obj.relative_to(base_dir)).replace("\\", "/")
            
            # Label'ı güncelle
            if tip == "ogrenci":
                self.ogrenci_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "ogretmen":
                self.ogretmen_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "cikis":
                self.cikis_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "mars":
                self.mars_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "siren":
                self.siren_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "saygi":
                self.saygi_sound_label.setText(relative_path.replace("\\", "/"))
            elif tip == "siren_mars_siren":
                self.siren_mars_siren_label.setText(relative_path.replace("\\", "/"))
            elif tip == "siren_mars_mars":
                self.siren_mars_mars_label.setText(relative_path.replace("\\", "/"))
    
    def _update_startup(self, enable: bool):
        """Windows startup klasörüne kısayol ekle/çıkar"""
        try:
            import os
            
            # Startup klasörü yolu
            startup_folder = os.path.join(
                os.environ.get("APPDATA"),
                "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )
            
            # Klasörü oluştur (yoksa)
            os.makedirs(startup_folder, exist_ok=True)
            
            # Ana program yolunu bul
            base_dir = Path(__file__).parent.parent
            main_py = base_dir / "main.py"
            
            # .bat dosyası yolu
            bat_name = "Okul_Zili.bat"
            bat_path = os.path.join(startup_folder, bat_name)
            
            if enable:
                # .bat dosyası oluştur
                # Python yolunu bul
                python_exe = sys.executable
                
                # .bat içeriği
                bat_content = f'''@echo off
cd /d "{base_dir}"
"{python_exe}" "{main_py}"
'''
                
                with open(bat_path, 'w', encoding='utf-8') as f:
                    f.write(bat_content)
            else:
                # .bat dosyasını sil
                if os.path.exists(bat_path):
                    try:
                        os.remove(bat_path)
                    except Exception as e:
                        QMessageBox.warning(self, "Uyarı", f"Startup dosyası silinemedi:\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Otomatik başlatma ayarı uygulanamadı:\n{e}")
    
    def get_settings(self) -> dict:
        """Ayarları döndür"""
        return self.settings_data
