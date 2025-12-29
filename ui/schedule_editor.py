"""
Ders Programı Oluşturucu ve Editörü
"""
import json
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QComboBox, QTimeEdit, QTableWidget,
    QTableWidgetItem, QMessageBox, QTabWidget, QWidget,
    QGroupBox, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QColor



class ScheduleEditor(QDialog):
    """Ders programı oluşturma ve düzenleme penceresi"""
    
    def __init__(self, schedule_file: str = "data/schedule.json", settings_file: str = "data/settings.json", parent=None):
        super().__init__(parent)
        # Çalışma dizinini bul
        base_dir = Path(__file__).parent.parent
        self.schedule_file = base_dir / schedule_file
        self.settings_file = base_dir / settings_file
        self.schedule_data: Dict = {}
        self.settings_data: Dict = {}
        self.defaults: Dict = {}
        
        self.setWindowTitle("Ders Programı Oluşturucu")
        
        # Ekran boyutuna göre pencere boyutunu ayarla
        screen = self.screen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Maksimum boyut: ekran boyutunun %90'ı
        max_width = int(screen_width * 0.95)
        max_height = int(screen_height * 0.90)
        
        # Minimum ve başlangıç boyutu
        min_width = 800
        min_height = 600
        start_width = min(max_width, 1000)
        start_height = min(max_height, 750)
        
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
        
        self._load_schedule()
        self._load_settings()
        self._setup_ui()
    
    def _setup_ui(self):
        """UI'ı oluştur"""
        layout = QVBoxLayout()
        
        # Sekmeler
        self.tabs = QTabWidget()
        
        # 1. Hızlı Oluşturma Sekmesi
        hizli_tab = self._create_quick_setup_tab()
        self.tabs.addTab(hizli_tab, "Hızlı Oluştur")
        
        # 2. Gelişmiş Oluşturma Sekmesi
        gelismis_tab = self._create_advanced_setup_tab()
        self.tabs.addTab(gelismis_tab, "Gelişmiş Oluştur")
        
        # 3. Standart Ayarlar Sekmesi
        defaults_tab = self._create_defaults_tab()
        self.tabs.addTab(defaults_tab, "Standart Ayarlar")
        
        # 4. Tablo Editörü Sekmesi
        editor_tab = self._create_table_editor_tab()
        self.tabs.addTab(editor_tab, "Tablo Editörü")
        
        layout.addWidget(self.tabs)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        buttons_layout.addStretch()
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )
        button_box.accepted.connect(self._save_and_close)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply_changes)
        buttons_layout.addWidget(button_box)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def _create_quick_setup_tab(self) -> QWidget:
        """Hızlı oluşturma sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Bilgi
        info_label = QLabel(
            "<b>Hızlı Mod:</b> Temel bilgileri girerek otomatik program oluşturun.<br>"
            "Program tüm günler için aynı saatleri kullanır."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Parametreler
        params_group = QGroupBox("Program Parametreleri")
        params_layout = QFormLayout()
        
        # İlk ders başlangıç saati
        self.ilk_ders_saat = QTimeEdit()
        self.ilk_ders_saat.setTime(QTime(8, 30))
        self.ilk_ders_saat.setDisplayFormat("HH:mm")
        params_layout.addRow("İlk Ders Başlangıç:", self.ilk_ders_saat)
        
        # Ders sayısı
        self.ders_sayisi = QSpinBox()
        self.ders_sayisi.setRange(1, 12)
        self.ders_sayisi.setValue(6)
        params_layout.addRow("Günlük Ders Sayısı:", self.ders_sayisi)
        
        # Ders süresi
        self.ders_suresi = QSpinBox()
        self.ders_suresi.setRange(30, 90)
        self.ders_suresi.setValue(40)
        self.ders_suresi.setSuffix(" dakika")
        params_layout.addRow("Ders Süresi:", self.ders_suresi)
        
        # Teneffüs süresi
        self.teneffus_suresi = QSpinBox()
        self.teneffus_suresi.setRange(5, 30)
        self.teneffus_suresi.setValue(10)
        self.teneffus_suresi.setSuffix(" dakika")
        params_layout.addRow("Teneffüs Süresi:", self.teneffus_suresi)
        
        # Öğle arası
        self.ogle_arasi_check = QCheckBox("Öğle arası var")
        self.ogle_arasi_check.setChecked(True)
        params_layout.addRow("", self.ogle_arasi_check)
        
        self.ogle_arasi_dersten_sonra = QSpinBox()
        self.ogle_arasi_dersten_sonra.setRange(1, 12)
        self.ogle_arasi_dersten_sonra.setValue(4)
        params_layout.addRow("Öğle Arası (Kaçıncı Dersten Sonra):", self.ogle_arasi_dersten_sonra)
        
        self.ogle_arasi_suresi = QSpinBox()
        self.ogle_arasi_suresi.setRange(30, 120)
        self.ogle_arasi_suresi.setValue(60)
        self.ogle_arasi_suresi.setSuffix(" dakika")
        params_layout.addRow("Öğle Arası Süresi:", self.ogle_arasi_suresi)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Aktif günler
        gunler_group = QGroupBox("Aktif Günler")
        gunler_layout = QVBoxLayout()
        
        self.gun_checkboxes = {}
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for gun in gunler:
            checkbox = QCheckBox(gun)
            if gun in ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]:
                checkbox.setChecked(True)
            self.gun_checkboxes[gun] = checkbox
            gunler_layout.addWidget(checkbox)
        
        gunler_group.setLayout(gunler_layout)
        layout.addWidget(gunler_group)
        
        # Oluştur butonu
        olustur_btn = QPushButton("Programı Oluştur")
        olustur_btn.clicked.connect(self._quick_create_schedule)
        olustur_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(olustur_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_advanced_setup_tab(self) -> QWidget:
        """Gelişmiş oluşturma sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "<b>Gelişmiş Mod:</b> Her gün için farklı program oluşturabilirsiniz.<br>"
            "Öğretmen giriş saatlerini de ayarlayabilirsiniz."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Gün seçimi
        gun_secim_group = QGroupBox("Düzenlenecek Gün")
        gun_secim_layout = QHBoxLayout()
        
        self.gun_secim_combo = QComboBox()
        self.gun_secim_combo.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        gun_secim_layout.addWidget(QLabel("Gün:"))
        gun_secim_layout.addWidget(self.gun_secim_combo)
        gun_secim_layout.addStretch()
        
        gun_secim_group.setLayout(gun_secim_layout)
        layout.addWidget(gun_secim_group)
        
        # Gelişmiş parametreler
        gelismis_group = QGroupBox("Gelişmiş Parametreler")
        gelismis_layout = QFormLayout()
        
        self.gelismis_ilk_ders = QTimeEdit()
        self.gelismis_ilk_ders.setTime(QTime(8, 30))
        self.gelismis_ilk_ders.setDisplayFormat("HH:mm")
        gelismis_layout.addRow("İlk Ders Başlangıç:", self.gelismis_ilk_ders)
        
        self.gelismis_ders_sayisi = QSpinBox()
        self.gelismis_ders_sayisi.setRange(1, 12)
        self.gelismis_ders_sayisi.setValue(6)
        gelismis_layout.addRow("Ders Sayısı:", self.gelismis_ders_sayisi)
        
        self.gelismis_ders_suresi = QSpinBox()
        self.gelismis_ders_suresi.setRange(30, 90)
        self.gelismis_ders_suresi.setValue(40)
        self.gelismis_ders_suresi.setSuffix(" dakika")
        gelismis_layout.addRow("Ders Süresi:", self.gelismis_ders_suresi)
        
        self.ogrenci_giris_farki = QSpinBox()
        self.ogrenci_giris_farki.setRange(0, 10)
        self.ogrenci_giris_farki.setValue(2)
        self.ogrenci_giris_farki.setSuffix(" dakika (ders başlangıcından önce)")
        gelismis_layout.addRow("Öğrenci Giriş Farkı:", self.ogrenci_giris_farki)
        
        self.gelismis_teneffus = QSpinBox()
        self.gelismis_teneffus.setRange(5, 30)
        self.gelismis_teneffus.setValue(10)
        self.gelismis_teneffus.setSuffix(" dakika")
        gelismis_layout.addRow("Teneffüs Süresi:", self.gelismis_teneffus)
        
        self.gelismis_ogle_check = QCheckBox("Öğle arası var")
        self.gelismis_ogle_check.setChecked(True)
        gelismis_layout.addRow("", self.gelismis_ogle_check)
        
        self.gelismis_ogle_dersten_sonra = QSpinBox()
        self.gelismis_ogle_dersten_sonra.setRange(1, 12)
        self.gelismis_ogle_dersten_sonra.setValue(4)
        gelismis_layout.addRow("Öğle Arası (Kaçıncı Dersten Sonra):", self.gelismis_ogle_dersten_sonra)
        
        self.gelismis_ogle_suresi = QSpinBox()
        self.gelismis_ogle_suresi.setRange(30, 120)
        self.gelismis_ogle_suresi.setValue(60)
        self.gelismis_ogle_suresi.setSuffix(" dakika")
        gelismis_layout.addRow("Öğle Arası Süresi:", self.gelismis_ogle_suresi)
        
        gelismis_group.setLayout(gelismis_layout)
        layout.addWidget(gelismis_group)
        
        # Oluştur butonu
        gelismis_olustur_btn = QPushButton("Seçili Gün İçin Program Oluştur")
        gelismis_olustur_btn.clicked.connect(self._advanced_create_schedule)
        gelismis_olustur_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(gelismis_olustur_btn)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_defaults_tab(self) -> QWidget:
        """Standart Ayarlar sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Açıklama
        info_label = QLabel(
            "Standart ayarlar tüm otomatik hesaplamalarda kullanılır.\n"
            "Teneffüs süreleri değiştiğinde sadece zamanlar ötelenir, süreler değişmez."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Ayarlar grubu
        defaults_group = QGroupBox("Standart Ayarlar")
        defaults_layout = QFormLayout()
        
        # İlk ders başlangıç saati
        self.defaults_ilk_ders = QTimeEdit()
        self.defaults_ilk_ders.setDisplayFormat("HH:mm")
        try:
            ilk_ders_time = QTime.fromString(self.defaults["ilk_ders_baslangic"], "HH:mm")
            self.defaults_ilk_ders.setTime(ilk_ders_time)
        except:
            self.defaults_ilk_ders.setTime(QTime(8, 30))
        defaults_layout.addRow("İlk Ders Başlangıç Saati:", self.defaults_ilk_ders)
        
        # Standart teneffüs süresi
        self.defaults_teneffus = QSpinBox()
        self.defaults_teneffus.setMinimum(1)
        self.defaults_teneffus.setMaximum(60)
        self.defaults_teneffus.setValue(self.defaults.get("standart_teneffus", 10))
        defaults_layout.addRow("Standart Teneffüs Süresi (dk):", self.defaults_teneffus)
        
        # Günlük ders sayısı
        self.defaults_ders_sayisi = QSpinBox()
        self.defaults_ders_sayisi.setMinimum(1)
        self.defaults_ders_sayisi.setMaximum(12)
        self.defaults_ders_sayisi.setValue(self.defaults.get("gunluk_ders_sayisi", 8))
        defaults_layout.addRow("Günlük Ders Sayısı:", self.defaults_ders_sayisi)
        
        # Öğle arası süresi
        self.defaults_ogle_arasi = QSpinBox()
        self.defaults_ogle_arasi.setMinimum(10)
        self.defaults_ogle_arasi.setMaximum(120)
        self.defaults_ogle_arasi.setValue(self.defaults.get("ogle_arasi_suresi", 40))
        defaults_layout.addRow("Öğle Arası Süresi (dk):", self.defaults_ogle_arasi)
        
        # Öğle arası kaçıncı dersten sonra
        self.defaults_ogle_ders_no = QSpinBox()
        self.defaults_ogle_ders_no.setMinimum(1)
        self.defaults_ogle_ders_no.setMaximum(12)
        self.defaults_ogle_ders_no.setValue(self.defaults.get("ogle_arasi_ders_no", 4))
        defaults_layout.addRow("Öğle Arası Kaçıncı Dersten Sonra:", self.defaults_ogle_ders_no)
        
        # Standart ders süresi
        self.defaults_ders_suresi = QSpinBox()
        self.defaults_ders_suresi.setMinimum(20)
        self.defaults_ders_suresi.setMaximum(60)
        self.defaults_ders_suresi.setValue(self.defaults.get("standart_ders_suresi", 40))
        defaults_layout.addRow("Standart Ders Süresi (dk):", self.defaults_ders_suresi)
        
        # Öğrenci giriş farkı
        self.defaults_ogrenci_farki = QSpinBox()
        self.defaults_ogrenci_farki.setMinimum(0)
        self.defaults_ogrenci_farki.setMaximum(10)
        self.defaults_ogrenci_farki.setValue(self.defaults.get("ogrenci_giris_farki", 2))
        defaults_layout.addRow("Öğrenci Giriş Farkı (dk):", self.defaults_ogrenci_farki)
        
        defaults_group.setLayout(defaults_layout)
        layout.addWidget(defaults_group)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        kaydet_btn = QPushButton("Ayarları Kaydet")
        kaydet_btn.clicked.connect(self._save_defaults)
        buttons_layout.addWidget(kaydet_btn)
        
        uygula_btn = QPushButton("Tüm Günler İçin Otomatik Program Oluştur")
        uygula_btn.clicked.connect(self._apply_to_all_days)
        buttons_layout.addWidget(uygula_btn)
        
        secili_btn = QPushButton("Sadece Seçili Gün İçin Oluştur")
        secili_btn.clicked.connect(self._apply_to_selected_day)
        buttons_layout.addWidget(secili_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _create_table_editor_tab(self) -> QWidget:
        """Tablo editörü sekmesi"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Gün seçimi ve Shift sistemi
        gun_layout = QHBoxLayout()
        gun_layout.addWidget(QLabel("Düzenlenecek Gün:"))
        
        self.editor_gun_combo = QComboBox()
        self.editor_gun_combo.addItems(["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
        self.editor_gun_combo.currentTextChanged.connect(self._load_day_to_table)
        gun_layout.addWidget(self.editor_gun_combo)
        
        gun_layout.addSpacing(20)
        gun_layout.addWidget(QLabel("Mod:"))
        
        self.shift_mode_combo = QComboBox()
        self.shift_mode_combo.addItems(["Normal", "Sabahçı-Öğlenci"])
        self.shift_mode_combo.currentTextChanged.connect(self._on_shift_mode_changed)
        gun_layout.addWidget(self.shift_mode_combo)
        
        self.shift_select_combo = QComboBox()
        self.shift_select_combo.addItems(["Sabahçı", "Öğlenci"])
        self.shift_select_combo.currentTextChanged.connect(self._load_day_to_table)
        self.shift_select_combo.setVisible(False)
        gun_layout.addWidget(self.shift_select_combo)
        
        aktif_check = QCheckBox("Bu gün aktif")
        aktif_check.setChecked(True)
        self.editor_aktif_check = aktif_check
        aktif_check.toggled.connect(self._toggle_day_active)
        gun_layout.addWidget(aktif_check)
        
        gun_layout.addStretch()
        layout.addLayout(gun_layout)
        
        # Tablo - Her satır bir ders
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Ders No", "Öğrenci Giriş", "Öğretmen Giriş", "Ders Çıkış", "Sonraki Teneffüs (dk)", "Ses Dosyası"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        # Tablo hücre değişikliklerini kontrol et
        self.table.itemChanged.connect(self._on_table_item_changed)
        layout.addWidget(self.table)
        
        # Tablo butonları
        table_buttons = QHBoxLayout()
        
        ekle_btn = QPushButton("Ders Ekle")
        ekle_btn.clicked.connect(self._add_lesson_row)
        table_buttons.addWidget(ekle_btn)
        
        sil_btn = QPushButton("Seçili Dersi Sil")
        sil_btn.clicked.connect(self._remove_lesson_row)
        table_buttons.addWidget(sil_btn)
        
        table_buttons.addSpacing(20)
        
        # Bu günü diğer günlere kopyala butonu
        kopyala_btn = QPushButton("Bu Günü Diğer Günlere Kopyala")
        kopyala_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        kopyala_btn.clicked.connect(self._copy_day_to_others)
        table_buttons.addWidget(kopyala_btn)
        
        table_buttons.addStretch()
        layout.addLayout(table_buttons)
        
        # İlk günü yükle
        self._load_day_to_table()
        
        widget.setLayout(layout)
        return widget
    
    def _quick_create_schedule(self):
        """Hızlı modda program oluştur"""
        ilk_ders = self.ilk_ders_saat.time()
        ders_sayisi = self.ders_sayisi.value()
        ders_suresi = self.ders_suresi.value()
        teneffus_suresi = self.teneffus_suresi.value()
        ogle_var = self.ogle_arasi_check.isChecked()
        ogle_dersten_sonra = self.ogle_arasi_dersten_sonra.value()
        ogle_suresi = self.ogle_arasi_suresi.value()
        
        # Aktif günleri al
        aktif_gunler = [gun for gun, checkbox in self.gun_checkboxes.items() if checkbox.isChecked()]
        
        if not aktif_gunler:
            QMessageBox.warning(self, "Uyarı", "En az bir gün seçmelisiniz!")
            return
        
        # Her aktif gün için program oluştur
        for gun in aktif_gunler:
            lessons = self._calculate_lessons(
                ilk_ders, ders_sayisi, ders_suresi, teneffus_suresi,
                ogle_var, ogle_dersten_sonra, ogle_suresi, 2  # Öğrenci 2 dk önce
            )
            
            self.schedule_data["days"][gun] = {
                "active": True,
                "lessons": lessons
            }
        
        # Tablo editörüne yükle
        self.editor_gun_combo.setCurrentIndex(0)
        self._load_day_to_table()
        
        QMessageBox.information(self, "Başarılı", f"{len(aktif_gunler)} gün için program oluşturuldu!")
    
    def _advanced_create_schedule(self):
        """Gelişmiş modda program oluştur"""
        secili_gun = self.gun_secim_combo.currentText()
        ilk_ders = self.gelismis_ilk_ders.time()
        ders_sayisi = self.gelismis_ders_sayisi.value()
        ders_suresi = self.gelismis_ders_suresi.value()
        teneffus_suresi = self.gelismis_teneffus.value()
        ogrenci_farki = self.ogrenci_giris_farki.value()
        ogle_var = self.gelismis_ogle_check.isChecked()
        ogle_dersten_sonra = self.gelismis_ogle_dersten_sonra.value()
        ogle_suresi = self.gelismis_ogle_suresi.value()
        
        ogrenci_farki = self.ogrenci_giris_farki.value()
        lessons = self._calculate_lessons(
            ilk_ders, ders_sayisi, ders_suresi, teneffus_suresi,
            ogle_var, ogle_dersten_sonra, ogle_suresi, ogrenci_farki
        )
        
        self.schedule_data["days"][secili_gun] = {
            "active": True,
            "lessons": lessons
        }
        
        # Tablo editörüne yükle
        index = self.editor_gun_combo.findText(secili_gun)
        if index >= 0:
            self.editor_gun_combo.setCurrentIndex(index)
        self._load_day_to_table()
        
        QMessageBox.information(self, "Başarılı", f"{secili_gun} için program oluşturuldu!")
    
    def _calculate_lessons(self, ilk_ders: QTime, ders_sayisi: int, ders_suresi: int,
                          teneffus_suresi: int, ogle_var: bool, ogle_dersten_sonra: int,
                          ogle_suresi: int, ogrenci_farki: int) -> List[Dict]:
        """
        Ders saatlerini hesapla
        
        Mantık:
        - Öğretmen zili = Ders başlangıç saati (dersin gerçek başlangıcı)
        - Öğrenci zili = Ders başlangıcından X dakika önce (ogrenci_farki)
        - Ders çıkış = Ders başlangıcı + ders süresi
        - Sonraki ders başlangıcı = Önceki ders çıkış + teneffüs süresi
        """
        lessons = []
        # QTime'ı Python time objesine çevir
        ilk_ders_time = time(ilk_ders.hour(), ilk_ders.minute())
        # İlk dersin başlangıç saati (öğretmen zili)
        ders_baslangic = datetime.combine(datetime.today(), ilk_ders_time)
        
        for ders_no in range(1, ders_sayisi + 1):
            # Öğle arası kontrolü (belirtilen dersten SONRA öğle arası var)
            if ogle_var and ders_no == ogle_dersten_sonra + 1:
                # Önceki dersin çıkışından sonra öğle arası süresi ekle
                ders_baslangic += timedelta(minutes=ogle_suresi)
            
            # Öğretmen giriş = Ders başlangıç saati (dersin gerçek başlangıcı)
            ogretmen_giris = ders_baslangic
            
            # Öğrenci giriş = Ders başlangıcından X dakika önce
            ogrenci_giris = ders_baslangic - timedelta(minutes=ogrenci_farki)
            
            # Ders çıkış = Ders başlangıcı + ders süresi
            ders_cikis = ders_baslangic + timedelta(minutes=ders_suresi)
            
            lessons.append({
                "lesson": ders_no,
                "ogrenci_giris": ogrenci_giris.strftime("%H:%M"),
                "ogretmen_giris": ogretmen_giris.strftime("%H:%M"),  # Ders başlangıcı
                "ders_cikis": ders_cikis.strftime("%H:%M"),
                "sound": "ziller/zil1.mp3"
            })
            
            # Sonraki ders için zamanı güncelle
            # Sonraki ders başlangıcı = Bu ders çıkış + teneffüs süresi
            if ders_no < ders_sayisi:
                ders_baslangic = ders_cikis + timedelta(minutes=teneffus_suresi)
            else:
                ders_baslangic = ders_cikis
        
        return lessons
    
    def _on_shift_mode_changed(self, mode: str):
        """Shift modu değiştiğinde"""
        if not hasattr(self, 'editor_gun_combo') or not self.editor_gun_combo:
            return
        
        gun = self.editor_gun_combo.currentText()
        if not gun:
            return
        
        if mode == "Sabahçı-Öğlenci":
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                self.shift_select_combo.setVisible(True)
            
            # Eğer normal moddan shift moduna geçiliyorsa, mevcut lessons'ı sabahçı shift'ine kopyala
            if gun in self.schedule_data.get("days", {}):
                gun_data = self.schedule_data["days"][gun]
                if "lessons" in gun_data and "sabahci" not in gun_data:
                    # Normal lessons'ı sabahçı shift'ine kopyala
                    gun_data["sabahci"] = {
                        "active": gun_data.get("active", False),
                        "lessons": gun_data["lessons"].copy() if gun_data.get("lessons") else []
                    }
                    gun_data["oglenci"] = {
                        "active": False,
                        "lessons": []
                    }
                    gun_data["shift_ayirma_saati"] = "12:00"
        else:
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                self.shift_select_combo.setVisible(False)
            
            # Eğer shift modundan normal moda geçiliyorsa, sabahçı lessons'ı normal lessons'a kopyala
            if gun in self.schedule_data.get("days", {}):
                gun_data = self.schedule_data["days"][gun]
                if "sabahci" in gun_data and "lessons" not in gun_data:
                    # Sabahçı lessons'ı normal lessons'a kopyala
                    gun_data["lessons"] = gun_data["sabahci"]["lessons"].copy() if gun_data["sabahci"].get("lessons") else []
                    gun_data["active"] = gun_data["sabahci"].get("active", False)
        
        self._load_day_to_table()
    
    def _load_day_to_table(self):
        """Seçili günün derslerini tabloya yükle"""
        # Eğer combo henüz oluşturulmamışsa çık
        if not hasattr(self, 'editor_gun_combo') or not self.editor_gun_combo:
            return
        
        gun = self.editor_gun_combo.currentText()
        
        if not gun or gun not in self.schedule_data.get("days", {}):
            self.table.setRowCount(0)
            if hasattr(self, 'editor_aktif_check'):
                self.editor_aktif_check.setChecked(False)
            # Shift modunu kontrol et
            self._update_shift_mode_combo(gun)
            return
        
        gun_data = self.schedule_data["days"][gun]
        
        # Shift modunu kontrol et ve combo'yu güncelle
        self._update_shift_mode_combo(gun)
        
        # Aktif durumu ayarla
        if "sabahci" in gun_data and "oglenci" in gun_data:
            # Shift sistemi aktif
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                shift = self.shift_select_combo.currentText().lower()
            else:
                shift = "sabahçı"  # Varsayılan
            if shift == "sabahçı":
                shift_data = gun_data.get("sabahci", {"active": False, "lessons": []})
            else:
                shift_data = gun_data.get("oglenci", {"active": False, "lessons": []})
            if hasattr(self, 'editor_aktif_check') and self.editor_aktif_check:
                self.editor_aktif_check.setChecked(shift_data.get("active", False))
            lessons = shift_data.get("lessons", [])
        else:
            # Normal mod
            if hasattr(self, 'editor_aktif_check') and self.editor_aktif_check:
                self.editor_aktif_check.setChecked(gun_data.get("active", False))
            lessons = gun_data.get("lessons", [])
        # Tablo yüklenirken signal'ları blokla (otomatik uyarıları önlemek için)
        self.table.blockSignals(True)
        self.table.setRowCount(len(lessons))
        
        for row, lesson in enumerate(lessons):
            ders_no = lesson.get("lesson", row + 1)
            ogrenci = lesson.get("ogrenci_giris", "08:28")
            ogretmen = lesson.get("ogretmen_giris", "08:30")
            cikis = lesson.get("ders_cikis", "09:10")
            
            # Ders No
            self.table.setItem(row, 0, QTableWidgetItem(str(ders_no)))
            
            # Öğrenci Giriş
            self.table.setItem(row, 1, QTableWidgetItem(ogrenci))
            
            # Öğretmen Giriş
            self.table.setItem(row, 2, QTableWidgetItem(ogretmen))
            
            # Ders Çıkış
            self.table.setItem(row, 3, QTableWidgetItem(cikis))
            
            # Teneffüs Süresi (son ders hariç)
            if row < len(lessons) - 1:
                # Sonraki dersin öğrenci girişi ile bu dersin çıkışı arasındaki fark
                try:
                    cikis_dt = datetime.strptime(cikis, "%H:%M")
                    sonraki_ogrenci = lessons[row + 1].get("ogrenci_giris", "")
                    if not sonraki_ogrenci:
                        teneffus_suresi = 10  # Varsayılan
                    else:
                        sonraki_ogrenci_dt = datetime.strptime(sonraki_ogrenci, "%H:%M")
                        teneffus_suresi = int((sonraki_ogrenci_dt - cikis_dt).total_seconds() / 60)
                        # Negatif değer kontrolü
                        if teneffus_suresi < 0:
                            teneffus_suresi = 10  # Varsayılan
                except:
                    teneffus_suresi = 10  # Varsayılan
                
                # Teneffüs süresi - öğle arası kontrolü kaldırıldı, normal teneffüs gibi gösteriliyor
                teneffus_item = QTableWidgetItem(str(teneffus_suresi))
                teneffus_item.setToolTip("Sonraki derse kadar olan teneffüs süresi (dakika)")
            else:
                teneffus_item = QTableWidgetItem("-")
                teneffus_item.setToolTip("Son ders - teneffüs yok")
            self.table.setItem(row, 4, teneffus_item)
            
            # Ses Dosyası
            self.table.setItem(row, 5, QTableWidgetItem(lesson.get("sound", "ziller/zil1.mp3")))
        
        # Signal'ları tekrar aç
        self.table.blockSignals(False)
    
    def _update_shift_mode_combo(self, gun: str):
        """Shift modu combo'sunu güncelle"""
        if not hasattr(self, 'shift_mode_combo') or not self.shift_mode_combo:
            return
        
        if not gun or gun not in self.schedule_data.get("days", {}):
            self.shift_mode_combo.setCurrentText("Normal")
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                self.shift_select_combo.setVisible(False)
            return
        
        gun_data = self.schedule_data["days"][gun]
        if "sabahci" in gun_data and "oglenci" in gun_data:
            self.shift_mode_combo.setCurrentText("Sabahçı-Öğlenci")
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                self.shift_select_combo.setVisible(True)
        else:
            self.shift_mode_combo.setCurrentText("Normal")
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                self.shift_select_combo.setVisible(False)
    
    def _on_table_item_changed(self, item: QTableWidgetItem):
        """Tablo hücresi değiştiğinde çağrılır"""
        # Önce doğrulama yap
        self._validate_table_item(item)
        
        # Signal blocking kontrolü - eğer zaten bloklanmışsa işlem yapma
        if self.table.signalsBlocked():
            return
        
        # Teneffüs süresi değiştiyse otomatik hesaplama yap (sütun 4)
        if item.column() == 4:
            text = item.text().strip()
            if text == "-":
                return  # Son ders, işlem yok
            
            # Öğle arası formatından sayıyı çıkar (varsa)
            if "(" in text and "Öğle" in text:
                text = text.split("(")[0].strip()
            
            try:
                sure = int(text)
                if 1 <= sure <= 60:
                    # Zaman öteleme mantığı: Teneffüs süresi değişti, sadece zaman ötelenir
                    self._shift_time_after_teneffus_change(item.row())
            except:
                pass
        
        # Saat değiştiyse sonraki dersleri güncelle
        elif item.column() in [1, 2, 3]:
            # Öğrenci giriş, öğretmen giriş veya çıkış değişti
            # Önce önceki dersin teneffüsünü güncelle (eğer varsa)
            if item.row() > 0:
                self._update_previous_teneffus(item.row())
            
            # Sonra sonraki dersin başlangıcını güncelle (zaman öteleme)
            if item.row() < self.table.rowCount() - 1:
                self._shift_time_after_saat_change(item.row())
    
    def _validate_table_item(self, item: QTableWidgetItem):
        """Tablo hücresindeki değeri doğrula"""
        # Teneffüs süresi sütunu (4)
        if item.column() == 4:
            text = item.text().strip()
            if text == "-":
                item.setBackground(QColor(255, 255, 255))
                return
            
            # Öğle arası kontrolü kaldırıldı - artık düzenlenebilir
            
            # Öğle arası formatı kontrolü (örn: "40 (Öğle)")
            if "(" in text and "Öğle" in text:
                text = text.split("(")[0].strip()
            
            try:
                sure = int(text)
                if 1 <= sure <= 60:
                    item.setBackground(QColor(255, 255, 255))
                    item.setToolTip("")
                else:
                    item.setBackground(QColor(255, 200, 200))
                    item.setToolTip("Teneffüs süresi 1-60 dakika arasında olmalı")
            except:
                item.setBackground(QColor(255, 200, 200))
                item.setToolTip("Geçerli bir sayı girin (örn: 15)")
            return
        
        # Saat sütunları (1, 2, 3) için format kontrolü ve otomatik dönüşüm
        if item.column() in [1, 2, 3]:
            text = item.text().strip()
            
            # HH:MM formatını kontrol et
            import re
            if re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', text):
                # Zaten doğru formatta
                item.setBackground(QColor(255, 255, 255))  # Beyaz
                item.setToolTip("")
            else:
                # Otomatik format dönüşümü dene
                # Örnek: 830 -> 08:30, 1430 -> 14:30, 930 -> 09:30
                formatted_time = self._auto_format_time(text)
                if formatted_time:
                    # Signal'ları blokla ve formatlanmış değeri yaz
                    self.table.blockSignals(True)
                    item.setText(formatted_time)
                    item.setBackground(QColor(255, 255, 255))  # Beyaz
                    item.setToolTip("")
                    self.table.blockSignals(False)
                else:
                    item.setBackground(QColor(255, 200, 200))  # Açık kırmızı
                    item.setToolTip("Geçersiz format! HH:MM formatında girin (örn: 08:30) veya sadece rakam (örn: 830)")
    
    def _auto_format_time(self, text: str) -> str:
        """Rakamları otomatik olarak saat formatına dönüştür (830 -> 08:30, 1430 -> 14:30)"""
        # Sadece rakam kontrolü
        if not text.isdigit():
            return None
        
        # 3-4 haneli rakamlar için
        if len(text) == 3:
            # 830 -> 08:30
            saat = int(text[0])
            dakika = int(text[1:3])
            if 0 <= saat <= 9 and 0 <= dakika <= 59:
                return f"{saat:02d}:{dakika:02d}"
        elif len(text) == 4:
            # 1430 -> 14:30
            saat = int(text[0:2])
            dakika = int(text[2:4])
            if 0 <= saat <= 23 and 0 <= dakika <= 59:
                return f"{saat:02d}:{dakika:02d}"
        
        return None
    
    def _save_defaults(self):
        """Standart ayarları kaydet"""
        self.defaults = {
            "ilk_ders_baslangic": self.defaults_ilk_ders.time().toString("HH:mm"),
            "standart_teneffus": self.defaults_teneffus.value(),
            "gunluk_ders_sayisi": self.defaults_ders_sayisi.value(),
            "ogle_arasi_suresi": self.defaults_ogle_arasi.value(),
            "ogle_arasi_ders_no": self.defaults_ogle_ders_no.value(),
            "standart_ders_suresi": self.defaults_ders_suresi.value(),
            "ogrenci_giris_farki": self.defaults_ogrenci_farki.value()
        }
        self._save_settings()
        QMessageBox.information(self, "Başarılı", "Standart ayarlar kaydedildi!")
    
    def _apply_to_all_days(self):
        """Tüm günler için otomatik program oluştur"""
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        for gun in gunler:
            self._create_auto_schedule(gun)
        QMessageBox.information(self, "Başarılı", "Tüm günler için program oluşturuldu!")
    
    def _apply_to_selected_day(self):
        """Seçili gün için otomatik program oluştur"""
        gun = self.editor_gun_combo.currentText()
        self._create_auto_schedule(gun)
        self._load_day_to_table()
        QMessageBox.information(self, "Başarılı", f"{gun} için program oluşturuldu!")
    
    def _create_auto_schedule(self, gun: str):
        """Standart ayarlara göre otomatik program oluştur"""
        if gun not in self.schedule_data.get("days", {}):
            self.schedule_data["days"][gun] = {"active": True, "lessons": []}
        
        lessons = []
        ilk_ders_baslangic = datetime.strptime(self.defaults["ilk_ders_baslangic"], "%H:%M")
        ogrenci_farki = self.defaults["ogrenci_giris_farki"]
        ders_suresi = self.defaults["standart_ders_suresi"]
        standart_teneffus = self.defaults["standart_teneffus"]
        gunluk_ders_sayisi = self.defaults["gunluk_ders_sayisi"]
        
        current_time = ilk_ders_baslangic
        
        for ders_no in range(1, gunluk_ders_sayisi + 1):
            # Öğrenci girişi (ders başlangıcından önce)
            ogrenci_giris = current_time - timedelta(minutes=ogrenci_farki)
            # Öğretmen girişi (ders başlangıcı)
            ogretmen_giris = current_time
            # Ders çıkışı
            ders_cikis = current_time + timedelta(minutes=ders_suresi)
            
            lessons.append({
                "lesson": ders_no,
                "ogrenci_giris": ogrenci_giris.strftime("%H:%M"),
                "ogretmen_giris": ogretmen_giris.strftime("%H:%M"),
                "ders_cikis": ders_cikis.strftime("%H:%M"),
                "sound": "ziller/zil1.mp3"
            })
            
            # Sonraki dersin başlangıcını hesapla
            if ders_no < gunluk_ders_sayisi:
                # Tüm teneffüsler standart teneffüs süresi kullanır (öğle arası kontrolü kaldırıldı)
                teneffus_suresi = standart_teneffus
                
                # Sonraki ders başlangıcı = Bu ders çıkışı + Teneffüs
                current_time = ders_cikis + timedelta(minutes=teneffus_suresi)
        
        self.schedule_data["days"][gun]["lessons"] = lessons
        self.schedule_data["days"][gun]["active"] = True
    
    def _shift_time_after_teneffus_change(self, ders_row: int):
        """Teneffüs süresi değiştiğinde sadece zaman ötele (süreler değişmez)"""
        if ders_row >= self.table.rowCount() - 1:
            return
        
        # Eski teneffüs süresini bulmak için önceki dersin çıkışı ile sonraki dersin öğrenci girişi arasındaki fark
        cikis_item = self.table.item(ders_row, 3)
        sonraki_ogrenci_item = self.table.item(ders_row + 1, 1)
        
        if not cikis_item or not sonraki_ogrenci_item:
            return
        
        try:
            ders_cikis = datetime.strptime(cikis_item.text().strip(), "%H:%M")
            eski_ogrenci_giris = datetime.strptime(sonraki_ogrenci_item.text().strip(), "%H:%M")
            eski_teneffus_suresi = int((eski_ogrenci_giris - ders_cikis).total_seconds() / 60)
        except:
            return
        
        # Yeni teneffüs süresi
        teneffus_item = self.table.item(ders_row, 4)
        if not teneffus_item:
            return
        
        try:
            teneffus_text = teneffus_item.text().strip()
            # Öğle arası formatından sayıyı çıkar
            if "(" in teneffus_text and "Öğle" in teneffus_text:
                teneffus_text = teneffus_text.split("(")[0].strip()
            yeni_teneffus_suresi = int(teneffus_text)
        except:
            return
        
        # Fark hesapla
        fark = yeni_teneffus_suresi - eski_teneffus_suresi
        
        # Sonraki dersin öğrenci girişi ötelenir
        yeni_ogrenci_giris = eski_ogrenci_giris + timedelta(minutes=fark)
        
        # Sonraki dersin mevcut saatlerinden farkları al
        sonraki_ders_row = ders_row + 1
        sonraki_ogretmen_item = self.table.item(sonraki_ders_row, 2)
        sonraki_cikis_item = self.table.item(sonraki_ders_row, 3)
        
        ogrenci_farki = self.defaults.get("ogrenci_giris_farki", 2)
        ders_suresi = self.defaults.get("standart_ders_suresi", 40)
        
        if sonraki_ogrenci_item and sonraki_ogretmen_item:
            try:
                ogrenci_dt = datetime.strptime(sonraki_ogrenci_item.text().strip(), "%H:%M")
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                ogrenci_farki = int((ogretmen_dt - ogrenci_dt).total_seconds() / 60)
            except:
                pass
        
        if sonraki_ogretmen_item and sonraki_cikis_item:
            try:
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                cikis_dt = datetime.strptime(sonraki_cikis_item.text().strip(), "%H:%M")
                ders_suresi = int((cikis_dt - ogretmen_dt).total_seconds() / 60)
            except:
                pass
        
        # Signal'i kapat
        self.table.blockSignals(True)
        
        # Sonraki dersin saatlerini ötelenmiş olarak güncelle
        sonraki_ogrenci_item.setText(yeni_ogrenci_giris.strftime("%H:%M"))
        
        yeni_ogretmen_giris = yeni_ogrenci_giris + timedelta(minutes=ogrenci_farki)
        if sonraki_ogretmen_item:
            sonraki_ogretmen_item.setText(yeni_ogretmen_giris.strftime("%H:%M"))
        
        yeni_cikis = yeni_ogretmen_giris + timedelta(minutes=ders_suresi)
        if sonraki_cikis_item:
            sonraki_cikis_item.setText(yeni_cikis.strftime("%H:%M"))
        
        # Sonraki teneffüs SÜRESİ değişmez, sadece zamanı ötelenir
        # Öğle arası kontrolü kaldırıldı - tüm teneffüsler normal teneffüs gibi işlenir
        
        self.table.blockSignals(False)
        
        # Recursive: Sonraki derslerin saatleri değişti, onların da sonraki derslerini ötelenir
        if sonraki_ders_row < self.table.rowCount() - 1:
            self._shift_time_after_teneffus_change(sonraki_ders_row)
    
    def _shift_time_after_saat_change(self, ders_row: int):
        """Saat değiştiğinde sadece zaman ötele (süreler değişmez)"""
        if ders_row >= self.table.rowCount() - 1:
            return
        
        # Bu dersin çıkışı ve teneffüsü
        cikis_item = self.table.item(ders_row, 3)
        teneffus_item = self.table.item(ders_row, 4)
        
        if not cikis_item or not teneffus_item:
            return
        
        try:
            ders_cikis = datetime.strptime(cikis_item.text().strip(), "%H:%M")
            teneffus_text = teneffus_item.text().strip()
            if teneffus_text == "-":
                return
            # Öğle arası formatından sayıyı çıkar
            if "(" in teneffus_text and "Öğle" in teneffus_text:
                teneffus_text = teneffus_text.split("(")[0].strip()
            teneffus_suresi = int(teneffus_text)
        except:
            return
        
        # Sonraki dersin öğrenci girişi
        sonraki_ogrenci_giris = ders_cikis + timedelta(minutes=teneffus_suresi)
        
        # Sonraki dersin mevcut saatlerinden farkları al
        sonraki_ders_row = ders_row + 1
        sonraki_ogrenci_item = self.table.item(sonraki_ders_row, 1)
        sonraki_ogretmen_item = self.table.item(sonraki_ders_row, 2)
        sonraki_cikis_item = self.table.item(sonraki_ders_row, 3)
        
        ogrenci_farki = self.defaults.get("ogrenci_giris_farki", 2)
        ders_suresi = self.defaults.get("standart_ders_suresi", 40)
        
        if sonraki_ogrenci_item and sonraki_ogretmen_item:
            try:
                ogrenci_dt = datetime.strptime(sonraki_ogrenci_item.text().strip(), "%H:%M")
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                ogrenci_farki = int((ogretmen_dt - ogrenci_dt).total_seconds() / 60)
            except:
                pass
        
        if sonraki_ogretmen_item and sonraki_cikis_item:
            try:
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                cikis_dt = datetime.strptime(sonraki_cikis_item.text().strip(), "%H:%M")
                ders_suresi = int((cikis_dt - ogretmen_dt).total_seconds() / 60)
            except:
                pass
        
        # Signal'i kapat
        self.table.blockSignals(True)
        
        # Sonraki dersin saatlerini ötelenmiş olarak güncelle
        if sonraki_ogrenci_item:
            sonraki_ogrenci_item.setText(sonraki_ogrenci_giris.strftime("%H:%M"))
        
        sonraki_ogretmen_giris = sonraki_ogrenci_giris + timedelta(minutes=ogrenci_farki)
        if sonraki_ogretmen_item:
            sonraki_ogretmen_item.setText(sonraki_ogretmen_giris.strftime("%H:%M"))
        
        sonraki_cikis = sonraki_ogretmen_giris + timedelta(minutes=ders_suresi)
        if sonraki_cikis_item:
            sonraki_cikis_item.setText(sonraki_cikis.strftime("%H:%M"))
        
        # Teneffüs süreleri değişmez, sadece zamanları ötelenir
        # Öğle arası kontrolü kaldırıldı - tüm teneffüsler normal teneffüs gibi işlenir
        
        self.table.blockSignals(False)
        
        # Recursive: Sonraki derslerin saatleri değişti
        if sonraki_ders_row < self.table.rowCount() - 1:
            self._shift_time_after_saat_change(sonraki_ders_row)
    
    def _recalculate_after_teneffus(self, ders_row: int):
        """Teneffüs süresi değiştiğinde sonraki dersleri yeniden hesapla"""
        if ders_row >= self.table.rowCount() - 1:
            return  # Son ders, teneffüs yok
        
        # Bu dersin çıkış saatini al
        cikis_item = self.table.item(ders_row, 3)
        if not cikis_item:
            return
        
        try:
            ders_cikis = datetime.strptime(cikis_item.text().strip(), "%H:%M")
        except:
            return
        
        # Teneffüs süresini al
        teneffus_item = self.table.item(ders_row, 4)
        if not teneffus_item:
            return
        
        try:
            teneffus_suresi = int(teneffus_item.text().strip())
        except:
            return
        
        # Sonraki dersin öğrenci giriş saatini hesapla
        sonraki_ogrenci_giris = ders_cikis + timedelta(minutes=teneffus_suresi)
        
        # Sonraki ders satırı
        sonraki_ders_row = ders_row + 1
        
        # Sonraki dersin mevcut saatlerini al (öğrenci-öğretmen farkı ve ders süresi için)
        sonraki_ogrenci_item = self.table.item(sonraki_ders_row, 1)
        sonraki_ogretmen_item = self.table.item(sonraki_ders_row, 2)
        sonraki_cikis_item = self.table.item(sonraki_ders_row, 3)
        
        # Öğrenci-öğretmen farkını hesapla (sonraki dersten)
        ogrenci_farki = 2  # Varsayılan
        if sonraki_ogrenci_item and sonraki_ogretmen_item:
            try:
                ogrenci_dt = datetime.strptime(sonraki_ogrenci_item.text().strip(), "%H:%M")
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                ogrenci_farki = int((ogretmen_dt - ogrenci_dt).total_seconds() / 60)
            except:
                pass
        
        # Ders süresini hesapla (sonraki dersten)
        ders_suresi = 40  # Varsayılan
        if sonraki_ogretmen_item and sonraki_cikis_item:
            try:
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                cikis_dt = datetime.strptime(sonraki_cikis_item.text().strip(), "%H:%M")
                ders_suresi = int((cikis_dt - ogretmen_dt).total_seconds() / 60)
            except:
                pass
        
        # Signal'i geçici olarak kapat
        self.table.blockSignals(True)
        
        # Sonraki dersin saatlerini güncelle
        if sonraki_ogrenci_item:
            sonraki_ogrenci_item.setText(sonraki_ogrenci_giris.strftime("%H:%M"))
        
        sonraki_ogretmen_giris = sonraki_ogrenci_giris + timedelta(minutes=ogrenci_farki)
        if sonraki_ogretmen_item:
            sonraki_ogretmen_item.setText(sonraki_ogretmen_giris.strftime("%H:%M"))
        
        sonraki_cikis = sonraki_ogretmen_giris + timedelta(minutes=ders_suresi)
        if sonraki_cikis_item:
            sonraki_cikis_item.setText(sonraki_cikis.strftime("%H:%M"))
        
        # Sonraki dersin teneffüsünü güncelle (varsa)
        if sonraki_ders_row < self.table.rowCount() - 1:
            sonraki_teneffus_item = self.table.item(sonraki_ders_row, 4)
            if sonraki_teneffus_item and sonraki_teneffus_item.text().strip() != "-":
                # Sonraki dersin çıkışı ile ondan sonraki dersin öğrenci girişi arasındaki fark
                sonraki_sonraki_ogrenci_item = self.table.item(sonraki_ders_row + 1, 1)
                if sonraki_sonraki_ogrenci_item:
                    try:
                        sonraki_sonraki_ogrenci_dt = datetime.strptime(sonraki_sonraki_ogrenci_item.text().strip(), "%H:%M")
                        yeni_teneffus_suresi = int((sonraki_sonraki_ogrenci_dt - sonraki_cikis).total_seconds() / 60)
                        if yeni_teneffus_suresi > 0:
                            sonraki_teneffus_item.setText(str(yeni_teneffus_suresi))
                    except:
                        pass
        
        # Signal'i tekrar aç
        self.table.blockSignals(False)
        
        # Recursive: Sonraki derslerin teneffüsünü de güncelle (sadece bir kez)
        # Bu çağrı sonraki dersin saatleri değiştiği için teneffüsünü güncellemek için
        if sonraki_ders_row < self.table.rowCount() - 1:
            # Sonraki dersin teneffüsü zaten güncellendi, sadece ondan sonraki dersleri güncelle
            self._recalculate_after_teneffus(sonraki_ders_row)
    
    def _update_previous_teneffus(self, ders_row: int):
        """Bir dersin saatleri değiştiğinde önceki dersin teneffüsünü güncelle"""
        if ders_row == 0:
            return  # İlk ders, önceki ders yok
        
        # Bu dersin öğrenci girişi
        ogrenci_item = self.table.item(ders_row, 1)
        if not ogrenci_item:
            return
        
        try:
            ogrenci_giris = datetime.strptime(ogrenci_item.text().strip(), "%H:%M")
        except:
            return
        
        # Önceki dersin çıkışı
        onceki_ders_row = ders_row - 1
        onceki_cikis_item = self.table.item(onceki_ders_row, 3)
        if not onceki_cikis_item:
            return
        
        try:
            onceki_cikis = datetime.strptime(onceki_cikis_item.text().strip(), "%H:%M")
        except:
            return
        
        # Teneffüs süresini hesapla
        teneffus_suresi = int((ogrenci_giris - onceki_cikis).total_seconds() / 60)
        
        # Önceki dersin teneffüsünü güncelle
        onceki_teneffus_item = self.table.item(onceki_ders_row, 4)
        if onceki_teneffus_item and teneffus_suresi > 0:
            self.table.blockSignals(True)
            onceki_teneffus_item.setText(str(teneffus_suresi))
            self.table.blockSignals(False)
    
    def _update_next_lesson_start(self, ders_row: int):
        """Bir dersin saatleri değiştiğinde sonraki dersin başlangıcını güncelle"""
        if ders_row >= self.table.rowCount() - 1:
            return  # Son ders
        
        # Bu dersin çıkışı ve teneffüsü
        cikis_item = self.table.item(ders_row, 3)
        teneffus_item = self.table.item(ders_row, 4)
        
        if not cikis_item or not teneffus_item:
            return
        
        try:
            ders_cikis = datetime.strptime(cikis_item.text().strip(), "%H:%M")
            teneffus_text = teneffus_item.text().strip()
            if teneffus_text == "-":
                return  # Son ders, teneffüs yok
            teneffus_suresi = int(teneffus_text)
        except:
            return
        
        # Sonraki dersin öğrenci girişi
        sonraki_ogrenci_giris = ders_cikis + timedelta(minutes=teneffus_suresi)
        
        # Sonraki dersin mevcut saatlerini al (öğrenci-öğretmen farkı ve ders süresi için)
        sonraki_ders_row = ders_row + 1
        sonraki_ogrenci_item = self.table.item(sonraki_ders_row, 1)
        sonraki_ogretmen_item = self.table.item(sonraki_ders_row, 2)
        sonraki_cikis_item = self.table.item(sonraki_ders_row, 3)
        
        # Öğrenci-öğretmen farkını hesapla (sonraki dersten)
        ogrenci_farki = 2  # Varsayılan
        if sonraki_ogrenci_item and sonraki_ogretmen_item:
            try:
                ogrenci_dt = datetime.strptime(sonraki_ogrenci_item.text().strip(), "%H:%M")
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                ogrenci_farki = int((ogretmen_dt - ogrenci_dt).total_seconds() / 60)
            except:
                pass
        
        # Ders süresini hesapla (sonraki dersten)
        ders_suresi = 40  # Varsayılan
        if sonraki_ogretmen_item and sonraki_cikis_item:
            try:
                ogretmen_dt = datetime.strptime(sonraki_ogretmen_item.text().strip(), "%H:%M")
                cikis_dt = datetime.strptime(sonraki_cikis_item.text().strip(), "%H:%M")
                ders_suresi = int((cikis_dt - ogretmen_dt).total_seconds() / 60)
            except:
                pass
        
        # Sonraki dersin saatlerini güncelle
        self.table.blockSignals(True)
        
        if sonraki_ogrenci_item:
            sonraki_ogrenci_item.setText(sonraki_ogrenci_giris.strftime("%H:%M"))
        
        sonraki_ogretmen_giris = sonraki_ogrenci_giris + timedelta(minutes=ogrenci_farki)
        if sonraki_ogretmen_item:
            sonraki_ogretmen_item.setText(sonraki_ogretmen_giris.strftime("%H:%M"))
        
        sonraki_cikis = sonraki_ogretmen_giris + timedelta(minutes=ders_suresi)
        if sonraki_cikis_item:
            sonraki_cikis_item.setText(sonraki_cikis.strftime("%H:%M"))
        
        # Sonraki dersin teneffüsünü güncelle (varsa)
        if sonraki_ders_row < self.table.rowCount() - 1:
            sonraki_teneffus_item = self.table.item(sonraki_ders_row, 4)
            if sonraki_teneffus_item and sonraki_teneffus_item.text().strip() != "-":
                sonraki_sonraki_ogrenci_item = self.table.item(sonraki_ders_row + 1, 1)
                if sonraki_sonraki_ogrenci_item:
                    try:
                        sonraki_sonraki_ogrenci_dt = datetime.strptime(sonraki_sonraki_ogrenci_item.text().strip(), "%H:%M")
                        yeni_teneffus_suresi = int((sonraki_sonraki_ogrenci_dt - sonraki_cikis).total_seconds() / 60)
                        if yeni_teneffus_suresi > 0:
                            sonraki_teneffus_item.setText(str(yeni_teneffus_suresi))
                    except:
                        pass
        
        self.table.blockSignals(False)
        
        # Sonraki derslerin saatleri değişti, onların da sonraki derslerini güncelle
        if sonraki_ders_row < self.table.rowCount() - 1:
            self._update_next_lesson_start(sonraki_ders_row)
    
    def _toggle_day_active(self, checked: bool):
        """Günün aktif/pasif durumunu değiştir"""
        gun = self.editor_gun_combo.currentText()
        if gun in self.schedule_data.get("days", {}):
            self.schedule_data["days"][gun]["active"] = checked
    
    def _add_lesson_row(self):
        """Tabloya yeni ders satırı ekle"""
        row_count = self.table.rowCount()
        ders_no = row_count + 1
        
        # Son dersin çıkış saatini al (varsa)
        son_ders_cikis = "09:10"  # Varsayılan
        if row_count > 0:
            son_cikis_item = self.table.item(row_count - 1, 3)
            if son_cikis_item:
                try:
                    son_cikis_dt = datetime.strptime(son_cikis_item.text().strip(), "%H:%M")
                    # Son dersin teneffüsünü al
                    son_teneffus_item = self.table.item(row_count - 1, 4)
                    teneffus_suresi = 10
                    if son_teneffus_item and son_teneffus_item.text().strip() != "-":
                        try:
                            teneffus_suresi = int(son_teneffus_item.text().strip())
                        except:
                            pass
                    # Yeni dersin öğrenci girişi = Son ders çıkış + teneffüs
                    yeni_ogrenci_dt = son_cikis_dt + timedelta(minutes=teneffus_suresi)
                    son_ders_cikis = yeni_ogrenci_dt.strftime("%H:%M")
                except:
                    pass
        
        # Ders satırı ekle
        self.table.insertRow(row_count)
        self.table.setItem(row_count, 0, QTableWidgetItem(str(ders_no)))
        self.table.setItem(row_count, 1, QTableWidgetItem(son_ders_cikis))  # Öğrenci giriş
        # Öğretmen giriş (öğrenci giriş + 2 dakika)
        try:
            ogrenci_dt = datetime.strptime(son_ders_cikis, "%H:%M")
            ogretmen_dt = ogrenci_dt + timedelta(minutes=2)
            self.table.setItem(row_count, 2, QTableWidgetItem(ogretmen_dt.strftime("%H:%M")))
            # Ders çıkış (öğretmen giriş + 40 dakika)
            cikis_dt = ogretmen_dt + timedelta(minutes=40)
            self.table.setItem(row_count, 3, QTableWidgetItem(cikis_dt.strftime("%H:%M")))
        except:
            self.table.setItem(row_count, 2, QTableWidgetItem("08:30"))
            self.table.setItem(row_count, 3, QTableWidgetItem("09:10"))
        
        # Teneffüs süresi (varsayılan 10 dakika)
        teneffus_item = QTableWidgetItem("10")
        teneffus_item.setToolTip("Sonraki derse kadar olan teneffüs süresi (dakika)")
        self.table.setItem(row_count, 4, teneffus_item)
        self.table.setItem(row_count, 5, QTableWidgetItem("ziller/zil1.mp3"))
    
    def _remove_lesson_row(self):
        """Seçili ders satırını sil"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz dersi seçin!")
    
    def _copy_day_to_others(self):
        """Seçili günün programını diğer günlere kopyala"""
        if not hasattr(self, 'editor_gun_combo') or not self.editor_gun_combo:
            return
        
        kaynak_gun = self.editor_gun_combo.currentText()
        if not kaynak_gun or kaynak_gun not in self.schedule_data.get("days", {}):
            QMessageBox.warning(self, "Uyarı", "Lütfen geçerli bir gün seçin!")
            return
        
        # Önce tablodaki değişiklikleri kaydet
        self._save_table_to_schedule()
        
        # Kaynak günün verilerini al
        kaynak_gun_data = self.schedule_data["days"][kaynak_gun]
        
        # Hangi günlere kopyalanacağını sor
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel, QDialogButtonBox
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        hedef_gunler = [g for g in gunler if g != kaynak_gun]
        
        # Dialog penceresi oluştur
        dialog = QDialog(self)
        dialog.setWindowTitle("Gün Seçimi")
        dialog.setMinimumWidth(300)
        dialog_layout = QVBoxLayout()
        
        dialog_layout.addWidget(QLabel(f"{kaynak_gun} gününü hangi günlere kopyalamak istersiniz?"))
        
        checkboxes = {}
        for gun in hedef_gunler:
            checkbox = QCheckBox(gun)
            checkbox.setChecked(True)  # Varsayılan olarak hepsi seçili
            checkboxes[gun] = checkbox
            dialog_layout.addWidget(checkbox)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(button_box)
        
        dialog.setLayout(dialog_layout)
        
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        # Seçili günleri al
        items = [gun for gun, checkbox in checkboxes.items() if checkbox.isChecked()]
        
        if not items:
            QMessageBox.warning(self, "Uyarı", "En az bir gün seçmelisiniz!")
            return
        
        # Shift sistemi kontrolü
        kaynak_shift_mode = "Normal"
        if "sabahci" in kaynak_gun_data and "oglenci" in kaynak_gun_data:
            kaynak_shift_mode = "Sabahçı-Öğlenci"
        
        # Her hedef güne kopyala
        for hedef_gun in items:
            if hedef_gun not in self.schedule_data.get("days", {}):
                self.schedule_data["days"][hedef_gun] = {"active": False, "lessons": []}
            
            hedef_gun_data = self.schedule_data["days"][hedef_gun]
            
            if kaynak_shift_mode == "Sabahçı-Öğlenci":
                # Shift sistemi - her iki shift'i de kopyala
                hedef_gun_data["sabahci"] = kaynak_gun_data["sabahci"].copy() if "sabahci" in kaynak_gun_data else {"active": False, "lessons": []}
                hedef_gun_data["oglenci"] = kaynak_gun_data["oglenci"].copy() if "oglenci" in kaynak_gun_data else {"active": False, "lessons": []}
                if "shift_ayirma_saati" in kaynak_gun_data:
                    hedef_gun_data["shift_ayirma_saati"] = kaynak_gun_data["shift_ayirma_saati"]
                # Normal lessons'ı temizle
                if "lessons" in hedef_gun_data:
                    del hedef_gun_data["lessons"]
            else:
                # Normal mod - lessons'ı kopyala
                hedef_gun_data["lessons"] = kaynak_gun_data["lessons"].copy() if "lessons" in kaynak_gun_data else []
                # Shift yapısını temizle
                if "sabahci" in hedef_gun_data:
                    del hedef_gun_data["sabahci"]
                if "oglenci" in hedef_gun_data:
                    del hedef_gun_data["oglenci"]
                if "shift_ayirma_saati" in hedef_gun_data:
                    del hedef_gun_data["shift_ayirma_saati"]
            
            hedef_gun_data["active"] = kaynak_gun_data.get("active", False)
        
        QMessageBox.information(self, "Başarılı", f"{kaynak_gun} günü {len(items)} güne kopyalandı!")
    
    def _save_table_to_schedule(self):
        """Tablodaki değişiklikleri schedule'a kaydet - Shift sistemi desteği"""
        if not hasattr(self, 'editor_gun_combo') or not self.editor_gun_combo:
            return
        
        gun = self.editor_gun_combo.currentText()
        if not gun:
            return
        
        if gun not in self.schedule_data.get("days", {}):
            self.schedule_data["days"][gun] = {"active": False, "lessons": []}
        
        lessons = []
        for row in range(self.table.rowCount()):
            ders_no_item = self.table.item(row, 0)
            ogrenci_item = self.table.item(row, 1)
            ogretmen_item = self.table.item(row, 2)
            cikis_item = self.table.item(row, 3)
            sound_item = self.table.item(row, 5)
            
            if not all([ders_no_item, ogrenci_item, ogretmen_item, cikis_item]):
                continue
            
            # Format kontrolü
            import re
            saat_format = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
            
            if not (saat_format.match(ogrenci_item.text().strip()) and 
                   saat_format.match(ogretmen_item.text().strip()) and 
                   saat_format.match(cikis_item.text().strip())):
                # Hata mesajı göster ama devam et
                continue
            
            # Ders numarası
            try:
                ders_no = int(ders_no_item.text().strip())
            except:
                ders_no = row + 1
            
            lessons.append({
                "lesson": ders_no,
                "ogrenci_giris": ogrenci_item.text().strip(),
                "ogretmen_giris": ogretmen_item.text().strip(),
                "ders_cikis": cikis_item.text().strip(),
                "sound": sound_item.text().strip() if sound_item else "ziller/zil1.mp3"
            })
        
        # Shift sistemi kontrolü
        if not hasattr(self, 'shift_mode_combo') or not self.shift_mode_combo:
            # Shift sistemi yoksa normal mod
            gun_data = self.schedule_data["days"][gun]
            gun_data["lessons"] = lessons
            gun_data["active"] = self.editor_aktif_check.isChecked() if hasattr(self, 'editor_aktif_check') else True
            return
        
        shift_mode = self.shift_mode_combo.currentText()
        gun_data = self.schedule_data["days"][gun]
        
        if shift_mode == "Sabahçı-Öğlenci":
            # Shift sistemi aktif
            if hasattr(self, 'shift_select_combo') and self.shift_select_combo:
                shift = self.shift_select_combo.currentText().lower()
            else:
                shift = "sabahçı"  # Varsayılan
            
            # Shift yapısını oluştur (eğer yoksa)
            if "sabahci" not in gun_data:
                gun_data["sabahci"] = {"active": False, "lessons": []}
            if "oglenci" not in gun_data:
                gun_data["oglenci"] = {"active": False, "lessons": []}
            
            # Shift ayırma saati (varsayılan 12:00)
            if "shift_ayirma_saati" not in gun_data:
                gun_data["shift_ayirma_saati"] = "12:00"
            
            # Seçili shift'e kaydet
            if shift == "sabahçı":
                gun_data["sabahci"]["lessons"] = lessons
                gun_data["sabahci"]["active"] = self.editor_aktif_check.isChecked() if hasattr(self, 'editor_aktif_check') and self.editor_aktif_check else True
            else:  # öğlenci
                gun_data["oglenci"]["lessons"] = lessons
                gun_data["oglenci"]["active"] = self.editor_aktif_check.isChecked() if hasattr(self, 'editor_aktif_check') and self.editor_aktif_check else True
            
            # Günün genel aktif durumu (en az bir shift aktifse)
            gun_data["active"] = gun_data["sabahci"].get("active", False) or gun_data["oglenci"].get("active", False)
            
            # Normal lessons'ı temizle (shift sistemi kullanılıyorsa)
            if "lessons" in gun_data:
                del gun_data["lessons"]
        else:
            # Normal mod
            gun_data["lessons"] = lessons
            gun_data["active"] = self.editor_aktif_check.isChecked() if hasattr(self, 'editor_aktif_check') else True
            
            # Shift yapısını temizle (normal mod kullanılıyorsa)
            if "sabahci" in gun_data:
                del gun_data["sabahci"]
            if "oglenci" in gun_data:
                del gun_data["oglenci"]
            if "shift_ayirma_saati" in gun_data:
                del gun_data["shift_ayirma_saati"]
    
    def _load_settings(self):
        """Ayarları yükle"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.settings_data = json.load(f)
            else:
                self.settings_data = {}
            
            # Standart ayarları al
            self.defaults = self.settings_data.get("schedule_defaults", {
                "ilk_ders_baslangic": "08:30",
                "standart_teneffus": 10,
                "gunluk_ders_sayisi": 8,
                "ogle_arasi_suresi": 40,
                "ogle_arasi_ders_no": 4,
                "standart_ders_suresi": 40,
                "ogrenci_giris_farki": 2
            })
        except Exception as e:
            # Varsayılan değerler
            self.defaults = {
                "ilk_ders_baslangic": "08:30",
                "standart_teneffus": 10,
                "gunluk_ders_sayisi": 8,
                "ogle_arasi_suresi": 40,
                "ogle_arasi_ders_no": 4,
                "standart_ders_suresi": 40,
                "ogrenci_giris_farki": 2
            }
    
    def _save_settings(self):
        """Ayarları kaydet"""
        try:
            if not self.settings_file.parent.exists():
                self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.settings_data["schedule_defaults"] = self.defaults
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Ayarlar kaydedilemedi: {str(e)}")
    
    def _load_schedule(self):
        """Mevcut programı yükle"""
        try:
            if self.schedule_file.exists():
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    self.schedule_data = json.load(f)
            else:
                self.schedule_data = self._default_schedule()
        except Exception as e:
            QMessageBox.warning(self, "Uyarı", f"Program yüklenirken hata: {e}")
            self.schedule_data = self._default_schedule()
    
    def _default_schedule(self) -> Dict:
        """Varsayılan program"""
        return {
            "days": {
                "Pazartesi": {"active": True, "lessons": []},
                "Salı": {"active": True, "lessons": []},
                "Çarşamba": {"active": True, "lessons": []},
                "Perşembe": {"active": True, "lessons": []},
                "Cuma": {"active": True, "lessons": []},
                "Cumartesi": {"active": False, "lessons": []},
                "Pazar": {"active": False, "lessons": []}
            },
            "special_scenarios": {}
        }
    
    def _apply_changes(self):
        """Değişiklikleri uygula (kaydet ama kapatma)"""
        self._save_table_to_schedule()
        self._save_to_file()
        QMessageBox.information(self, "Başarılı", "Değişiklikler kaydedildi!")
    
    def _save_and_close(self):
        """Değişiklikleri kaydet ve kapat"""
        self._save_table_to_schedule()
        self._save_to_file()
        self.accept()
    
    def _save_to_file(self):
        """Programı dosyaya kaydet"""
        try:
            self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(self.schedule_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Program kaydedilirken hata: {e}")
    
    def get_schedule_data(self) -> Dict:
        """Program verisini döndür"""
        self._save_table_to_schedule()
        return self.schedule_data
    
