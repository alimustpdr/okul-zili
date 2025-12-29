"""
Ana pencere - Tek bakışta her şey
"""
from datetime import datetime, timedelta
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame
)
from PySide6.QtCore import QTimer, Qt, Signal, QRect, QPoint
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor, QScreen, QPolygon

from core.scheduler import Scheduler
from core.sound_player import SoundPlayer
from core.state_manager import StateManager, ZilModu, ZilDurumu
from core.logger import ZilLogger
from ui.settings_window import SettingsWindow
from ui.schedule_editor import ScheduleEditor


class MainWindow(QMainWindow):
    """Ana pencere"""
    
    def __init__(self):
        super().__init__()
        
        # Core bileşenler
        self.logger = ZilLogger()
        self.state_manager = StateManager()
        self.sound_player = SoundPlayer()
        self.scheduler = Scheduler()
        
        # Scheduler sinyallerini bağla
        self.scheduler.zil_calindi.connect(self._on_zil_calindi)
        
        # Zamanlayıcılar
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)  # Her saniye güncelle
        
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self._update_countdown)
        self.countdown_timer.start(1000)
        
        self._setup_ui()
        self._load_settings()
        
        # Ekran boyutuna göre pencere boyutunu ayarla
        self._adjust_window_size()
        
        # Scheduler'ı başlat
        if self.state_manager.zil_calabilir_mi():
            self.scheduler.start()
        
        self.logger.log_sistem("Uygulama başlatıldı")
    
    def _adjust_window_size(self):
        """Pencere boyutunu ekran boyutuna göre ayarla"""
        screen = self.screen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Maksimum boyut: ekran boyutunun %90'ı (taskbar için yer bırak)
        max_width = int(screen_width * 0.95)
        max_height = int(screen_height * 0.90)
        
        # Minimum boyut
        min_width = 800
        min_height = 600
        
        # Başlangıç boyutu
        start_width = min(max_width, 1200)
        start_height = min(max_height, 800)
        
        self.setMinimumSize(min_width, min_height)
        self.setMaximumSize(max_width, max_height)
        self.resize(start_width, start_height)
        
        # Pencereyi ekranın ortasına yerleştir
        self.move(
            (screen_width - start_width) // 2,
            (screen_height - start_height) // 2
        )
    
    def _set_window_icon(self):
        """Pencere ikonunu ayarla"""
        icon = self._create_icon()
        self.setWindowIcon(icon)
    
    def _create_icon(self):
        """Profesyonel bir zil ikonu oluştur"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(0, 0, 0, 0))  # Şeffaf arka plan
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Zil şekli çiz (daha profesyonel bir çan)
        # Çan gövdesi
        painter.setBrush(QColor(70, 130, 180))  # Çelik mavisi
        painter.setPen(QColor(50, 100, 150))
        # Çan şekli için yuvarlak üst kısım
        painter.drawEllipse(12, 8, 40, 36)
        
        # Çan alt kısmı (açık kısım)
        painter.setBrush(QColor(100, 150, 200))
        painter.drawEllipse(16, 20, 32, 28)
        
        # Zil dili (çan içindeki top)
        painter.setBrush(QColor(200, 200, 200))
        painter.setPen(QColor(150, 150, 150))
        painter.drawEllipse(28, 36, 8, 8)
        
        # Zil askısı (üstteki halka)
        painter.setPen(QColor(100, 100, 100))
        painter.setBrush(QColor(120, 120, 120))
        painter.drawEllipse(28, 4, 8, 8)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_student_bell_icon(self):
        """Öğrenci zili ikonu - Mavi zil"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Mavi zil çanı
        painter.setBrush(QColor(33, 150, 243))
        painter.setPen(QColor(25, 118, 210))
        # Çan şekli (üst yuvarlak, alt geniş)
        painter.drawEllipse(8, 4, 32, 32)
        # Zil dili
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(20, 28, 8, 8)
        painter.end()
        return QIcon(pixmap)
    
    def _create_teacher_bell_icon(self):
        """Öğretmen zili ikonu - Turuncu zil"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Turuncu zil çanı
        painter.setBrush(QColor(255, 152, 0))
        painter.setPen(QColor(245, 124, 0))
        # Çan şekli
        painter.drawEllipse(8, 4, 32, 32)
        # Zil dili
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(20, 28, 8, 8)
        painter.end()
        return QIcon(pixmap)
    
    def _create_exit_bell_icon(self):
        """Çıkış zili ikonu - Yeşil ok"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Yeşil ok
        painter.setBrush(QColor(76, 175, 80))
        painter.setPen(QColor(56, 142, 60))
        # Ok şekli (üçgen)
        from PySide6.QtGui import QPolygon
        points = QPolygon([
            QPoint(12, 20),
            QPoint(28, 20),
            QPoint(20, 12),
            QPoint(20, 28)
        ])
        painter.drawPolygon(points)
        # Ok ucu
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(26, 18, 4, 4)
        painter.end()
        return QIcon(pixmap)
    
    def _create_turk_flag_icon(self):
        """Türk bayrağı ikonu - Daha net"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Kırmızı arka plan
        painter.setBrush(QColor(227, 10, 23))
        painter.setPen(QColor(200, 0, 0))
        painter.drawRect(4, 4, 40, 40)
        # Ay (beyaz)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(10, 12, 16, 16)
        # Ay içi (kırmızı)
        painter.setBrush(QColor(227, 10, 23))
        painter.drawEllipse(12, 12, 16, 16)
        # Yıldız (beyaz)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(30, 10, 12, 12)
        painter.end()
        return QIcon(pixmap)
    
    def _create_siren_icon(self):
        """Siren ikonu - Daha net"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Kırmızı siren çemberi
        painter.setBrush(QColor(244, 67, 54))
        painter.setPen(QColor(198, 40, 40))
        painter.drawEllipse(8, 8, 32, 32)
        # Dalga çizgileri (beyaz)
        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255))
        for i in range(3):
            y = 14 + i * 10
            painter.drawArc(12, y, 24, 12, 0, 180 * 16)
        painter.end()
        return QIcon(pixmap)
    
    def _create_siren_mars_icon(self):
        """Siren + İstiklal Marşı ikonu - Kombine"""
        pixmap = QPixmap(48, 48)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Sol taraf siren (kırmızı çember)
        painter.setBrush(QColor(244, 67, 54))
        painter.setPen(QColor(198, 40, 40))
        painter.drawEllipse(4, 12, 20, 20)
        # Sağ taraf bayrak (kırmızı dikdörtgen)
        painter.setBrush(QColor(227, 10, 23))
        painter.setPen(QColor(200, 0, 0))
        painter.drawRect(24, 4, 20, 40)
        # Bayrak üzerinde ay ve yıldız
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(27, 10, 10, 10)
        painter.setBrush(QColor(227, 10, 23))
        painter.drawEllipse(28, 10, 10, 10)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(33, 8, 8, 8)
        painter.end()
        return QIcon(pixmap)
    
    def _create_stop_icon(self):
        """Durdur ikonu - Beyaz kare"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(255, 255, 255))
        painter.drawRect(8, 8, 16, 16)
        painter.end()
        return QIcon(pixmap)
    
    def _setup_ui(self):
        """UI'ı oluştur - Resimdeki tasarıma benzer"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setLayout(main_layout)
        
        # Sol panel - Saat ve kontroller (genişlik sınırlı, kompakt)
        left_panel = QWidget()
        left_panel.setMaximumWidth(420)  # Sol panel genişliğini sınırla
        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)  # Spacing'i azalt
        left_layout.setContentsMargins(5, 5, 5, 5)  # Margin'leri azalt
        left_panel.setLayout(left_layout)
        
        # Saat ve tarih kutusu - Resimdeki gibi temiz ve okunaklı, kompakt
        clock_frame = QFrame()
        clock_frame.setFrameShape(QFrame.Shape.Box)
        clock_frame.setLineWidth(2)
        clock_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        clock_layout = QVBoxLayout()
        clock_layout.setSpacing(8)
        clock_layout.setContentsMargins(8, 8, 8, 8)
        
        # Tarih - Üstte tek satır, net ve okunaklı
        self.date_label = QLabel()
        date_font = QFont()
        date_font.setPointSize(12)
        date_font.setBold(False)
        self.date_label.setFont(date_font)
        self.date_label.setAlignment(Qt.AlignLeft)
        self.date_label.setStyleSheet("color: #333; padding: 5px 0px;")
        clock_layout.addWidget(self.date_label)
        
        # Saat ve küçük geri sayım - Yan yana
        time_countdown_layout = QHBoxLayout()
        time_countdown_layout.setSpacing(15)
        
        # Büyük saat - Sol taraf
        self.clock_label = QLabel("11:55")
        clock_font = QFont()
        clock_font.setPointSize(64)
        clock_font.setBold(True)
        self.clock_label.setFont(clock_font)
        self.clock_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.clock_label.setStyleSheet("color: #000; padding: 0px;")
        time_countdown_layout.addWidget(self.clock_label, 1)
        
        # Geri sayım (sağ üstte kırmızı kutu içinde)
        countdown_box = QFrame()
        countdown_box.setFrameShape(QFrame.Shape.Box)
        countdown_box.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #d32f2f;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 50px;
            }
        """)
        countdown_box_layout = QVBoxLayout()
        countdown_box_layout.setContentsMargins(5, 5, 5, 5)
        self.countdown_small_label = QLabel("07")
        countdown_small_font = QFont()
        countdown_small_font.setPointSize(20)
        countdown_small_font.setBold(True)
        self.countdown_small_label.setFont(countdown_small_font)
        self.countdown_small_label.setStyleSheet("color: #d32f2f; padding: 0px;")
        self.countdown_small_label.setAlignment(Qt.AlignCenter)
        countdown_box_layout.addWidget(self.countdown_small_label)
        countdown_box.setLayout(countdown_box_layout)
        time_countdown_layout.addWidget(countdown_box, 0)
        
        clock_layout.addLayout(time_countdown_layout)
        
        clock_frame.setLayout(clock_layout)
        left_layout.addWidget(clock_frame)
        
        # Zil durumu ve mod - Resimdeki gibi beyaz kutular içinde, kompakt
        status_layout = QVBoxLayout()
        status_layout.setSpacing(6)
        
        # Zil durumu - Beyaz kutu
        status_box = QFrame()
        status_box.setFrameShape(QFrame.Shape.Box)
        status_box.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        status_box_layout = QVBoxLayout()
        status_box_layout.setContentsMargins(4, 4, 4, 4)
        self.status_label = QLabel("Zil: AÇIK")
        self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold; font-size: 13pt; padding: 0px;")
        self.status_label.setAlignment(Qt.AlignLeft)
        status_box_layout.addWidget(self.status_label)
        status_box.setLayout(status_box_layout)
        status_layout.addWidget(status_box)
        
        # Mod - Beyaz kutu
        mode_box = QFrame()
        mode_box.setFrameShape(QFrame.Shape.Box)
        mode_box.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        mode_box_layout = QVBoxLayout()
        mode_box_layout.setContentsMargins(4, 4, 4, 4)
        self.mode_label = QLabel("Mod: Normal")
        self.mode_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 13pt; padding: 0px;")
        self.mode_label.setAlignment(Qt.AlignLeft)
        mode_box_layout.addWidget(self.mode_label)
        mode_box.setLayout(mode_box_layout)
        status_layout.addWidget(mode_box)
        
        left_layout.addLayout(status_layout)
        
        # Geri sayım bilgisi - Sarı banner (resimdeki gibi) - Daha kompakt
        self.countdown_label = QLabel("Sonraki zil: Hesaplanıyor...")
        countdown_desc_font = QFont()
        countdown_desc_font.setPointSize(10)
        countdown_desc_font.setBold(True)
        self.countdown_label.setFont(countdown_desc_font)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: #856404; 
            padding: 8px; 
            background-color: #fff3cd; 
            border: 2px solid #ffc107;
            border-radius: 5px;
        """)
        left_layout.addWidget(self.countdown_label)
        
        # Manuel butonlar - Tek sıra halinde, iki satır
        buttons_container = QWidget()
        buttons_container_layout = QVBoxLayout()
        buttons_container_layout.setContentsMargins(0, 0, 0, 0)
        buttons_container_layout.setSpacing(8)
        
        buttons_label = QLabel("<b>Manuel Kontroller</b>")
        buttons_label.setAlignment(Qt.AlignCenter)
        buttons_label.setStyleSheet("font-size: 13px; padding: 5px; font-weight: bold;")
        buttons_container_layout.addWidget(buttons_label)
        
        # İlk satır - Zil butonları (tek sıra)
        zil_buttons_layout = QHBoxLayout()
        zil_buttons_layout.setSpacing(8)
        zil_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_ogrenci = QPushButton("Öğrenci Zili")
        self.btn_ogrenci.clicked.connect(self._play_ogrenci_manuel)
        zil_buttons_layout.addWidget(self.btn_ogrenci)
        
        self.btn_ogretmen = QPushButton("Öğretmen Zili")
        self.btn_ogretmen.clicked.connect(self._play_ogretmen_manuel)
        zil_buttons_layout.addWidget(self.btn_ogretmen)
        
        self.btn_cikis = QPushButton("Çıkış Zili")
        self.btn_cikis.clicked.connect(self._play_cikis_manuel)
        zil_buttons_layout.addWidget(self.btn_cikis)
        
        buttons_container_layout.addLayout(zil_buttons_layout)
        
        # İkinci satır - Diğer butonlar (tek sıra)
        other_buttons_layout = QHBoxLayout()
        other_buttons_layout.setSpacing(8)
        other_buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_mars = QPushButton("İstiklal Marşı")
        self.btn_mars.clicked.connect(self._play_mars_manuel)
        other_buttons_layout.addWidget(self.btn_mars)
        
        self.btn_saygi = QPushButton("Saygı Duruşu\n+ İstiklal Marşı")
        self.btn_saygi.clicked.connect(self._play_saygi_durusu)
        other_buttons_layout.addWidget(self.btn_saygi)
        
        self.btn_siren = QPushButton("Siren")
        self.btn_siren.clicked.connect(self._play_siren_manuel)
        other_buttons_layout.addWidget(self.btn_siren)
        
        self.btn_siren_mars = QPushButton("Siren +\nİstiklal Marşı")
        self.btn_siren_mars.clicked.connect(self._play_siren_mars)
        other_buttons_layout.addWidget(self.btn_siren_mars)
        
        self.btn_durdur = QPushButton("DURDUR")
        self.btn_durdur.clicked.connect(self._stop_sound)
        other_buttons_layout.addWidget(self.btn_durdur)
        
        buttons_container_layout.addLayout(other_buttons_layout)
        
        # Buton stilleri - Tek sıra için optimize edilmiş, kompakt
        # Öğrenci zili - Açık mavi
        self.btn_ogrenci.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #E3F2FD;
                border: 2px solid #2196F3;
                min-height: 45px;
                color: #1976D2;
            }
            QPushButton:hover {
                background-color: #BBDEFB;
                border: 2px solid #1976D2;
            }
            QPushButton:pressed {
                background-color: #90CAF9;
            }
        """)
        
        # Öğretmen zili - Açık turuncu
        self.btn_ogretmen.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                min-height: 45px;
                color: #F57C00;
            }
            QPushButton:hover {
                background-color: #FFE0B2;
                border: 2px solid #F57C00;
            }
            QPushButton:pressed {
                background-color: #FFCC80;
            }
        """)
        
        # Çıkış zili - Açık yeşil
        self.btn_cikis.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #E8F5E9;
                border: 2px solid #4CAF50;
                min-height: 45px;
                color: #388E3C;
            }
            QPushButton:hover {
                background-color: #C8E6C9;
                border: 2px solid #388E3C;
            }
            QPushButton:pressed {
                background-color: #A5D6A7;
            }
        """)
        
        # İstiklal Marşı - Kırmızı
        self.btn_mars.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                min-height: 45px;
                color: #C62828;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
                border: 2px solid #C62828;
            }
            QPushButton:pressed {
                background-color: #EF9A9A;
            }
        """)
        
        # Saygı Duruşu + İstiklal Marşı - Kırmızı
        self.btn_saygi.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                min-height: 45px;
                color: #C62828;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
                border: 2px solid #C62828;
            }
            QPushButton:pressed {
                background-color: #EF9A9A;
            }
        """)
        
        # Siren - Kırmızı
        self.btn_siren.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                min-height: 45px;
                color: #C62828;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
                border: 2px solid #C62828;
            }
            QPushButton:pressed {
                background-color: #EF9A9A;
            }
        """)
        
        # Siren + İstiklal Marşı - Kırmızı
        self.btn_siren_mars.setStyleSheet("""
            QPushButton {
                padding: 8px 6px;
                font-size: 10px;
                font-weight: bold;
                border-radius: 5px;
                background-color: #FFEBEE;
                border: 2px solid #F44336;
                min-height: 45px;
                color: #C62828;
            }
            QPushButton:hover {
                background-color: #FFCDD2;
                border: 2px solid #C62828;
            }
            QPushButton:pressed {
                background-color: #EF9A9A;
            }
        """)
        
        # DURDUR butonu - Daha kompakt
        self.btn_durdur.setStyleSheet("""
            QPushButton {
                background-color: #d32f2f; 
                color: white; 
                font-weight: bold; 
                font-size: 12px; 
                padding: 8px; 
                border-radius: 5px;
                min-height: 45px;
            }
            QPushButton:hover {
                background-color: #b71c1c;
            }
            QPushButton:pressed {
                background-color: #8b0000;
            }
        """)
        
        buttons_container.setLayout(buttons_container_layout)
        
        # Butonları ekle - stretch yok, direkt ekle
        left_layout.addWidget(buttons_container)
        
        # Alt butonlar - Tek sıra halinde
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        bottom_layout.setContentsMargins(0, 5, 0, 0)
        
        self.btn_zil_ac_kapat = QPushButton("Zili Kapat")
        self.btn_zil_ac_kapat.setStyleSheet("padding: 8px; font-size: 11px; font-weight: bold; border-radius: 5px;")
        self.btn_zil_ac_kapat.clicked.connect(self._toggle_zil)
        bottom_layout.addWidget(self.btn_zil_ac_kapat)
        
        self.btn_ders_programi = QPushButton("Ders Programı")
        self.btn_ders_programi.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px; font-size: 11px; border-radius: 5px;")
        self.btn_ders_programi.clicked.connect(self._show_schedule_editor)
        bottom_layout.addWidget(self.btn_ders_programi)
        
        self.btn_ayarlar = QPushButton("Ayarlar")
        self.btn_ayarlar.setStyleSheet("padding: 8px; font-size: 11px; font-weight: bold; border-radius: 5px;")
        self.btn_ayarlar.clicked.connect(self._show_settings)
        bottom_layout.addWidget(self.btn_ayarlar)
        
        left_layout.addLayout(bottom_layout)
        
        # Alt boşluk yok - direkt ekle
        
        main_layout.addWidget(left_panel, 1)
        
        # Sağ panel - Ders programı
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)
        right_panel.setLayout(right_layout)
        
        # Geri sayım banner'ı - Resimdeki gibi sarı banner
        countdown_banner = QFrame()
        countdown_banner.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 2px solid #ffc107;
                border-radius: 5px;
                padding: 12px;
            }
        """)
        banner_layout = QHBoxLayout()
        banner_layout.setAlignment(Qt.AlignLeft)
        banner_layout.setSpacing(10)
        
        banner_icon = QLabel("⏰")
        banner_icon.setStyleSheet("font-size: 24px; padding: 0px;")
        banner_layout.addWidget(banner_icon, 0)
        
        self.countdown_banner_label = QLabel("1. Ders Öğrenci Giriş - 08:28")
        self.countdown_banner_label.setStyleSheet("font-weight: bold; font-size: 12pt; color: #856404; padding: 0px;")
        self.countdown_banner_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        banner_layout.addWidget(self.countdown_banner_label, 1)
        
        countdown_banner.setLayout(banner_layout)
        right_layout.addWidget(countdown_banner)
        
        # Ders programı başlığı
        schedule_title = QLabel("<b>Bugünün Ders Programı</b>")
        schedule_title.setStyleSheet("font-size: 13pt; padding: 5px;")
        schedule_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(schedule_title)
        
        # Ders programı tablosu - Resimdeki gibi
        self.today_schedule_table = QTableWidget()
        self.today_schedule_table.setColumnCount(4)
        self.today_schedule_table.setHorizontalHeaderLabels(["Ders", "Giriş Zili", "Öğretmen Zili", "Çıkış Zili"])
        self.today_schedule_table.horizontalHeader().setStretchLastSection(True)
        self.today_schedule_table.setAlternatingRowColors(True)
        self.today_schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.today_schedule_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.today_schedule_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: white;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #ddd;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        # Kolon genişliklerini ayarla
        header = self.today_schedule_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        right_layout.addWidget(self.today_schedule_table)
        
        right_layout.addStretch()
        
        main_layout.addWidget(right_panel, 2)
        
        # İlk güncelleme
        self._update_clock()
        self._update_countdown()
        self._update_status()
        
        self.setWindowTitle("Okul Zili")
        
        # Favicon ayarla
        self._set_window_icon()
    
    def _update_clock(self):
        """Saati güncelle"""
        simdi = datetime.now()
        self.clock_label.setText(simdi.strftime("%H:%M"))
        
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        ay_adi = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                  "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        gun_adi = gunler[simdi.weekday()]
        ay = ay_adi[simdi.month - 1]
        self.date_label.setText(f"{simdi.day} {ay} {simdi.year} {gun_adi}")
    
    def _update_countdown(self):
        """Geri sayımı güncelle"""
        # Bugünün programını göster
        self._update_today_schedule()
        
        if not self.state_manager.zil_calabilir_mi():
            if hasattr(self, 'countdown_small_label'):
                self.countdown_small_label.setText("--")
            if hasattr(self, 'countdown_banner_label'):
                self.countdown_banner_label.setText("Zil kapalı veya tatil modunda")
            if hasattr(self, 'countdown_label'):
                self.countdown_label.setText("Zil kapalı veya tatil modunda")
            return
        
        sonraki_zil = self.scheduler.get_next_zil()
        if sonraki_zil:
            simdi = datetime.now()
            fark = sonraki_zil["time"] - simdi
            
            if fark.total_seconds() < 0:
                if hasattr(self, 'countdown_small_label'):
                    self.countdown_small_label.setText("00")
                if hasattr(self, 'countdown_banner_label'):
                    self.countdown_banner_label.setText("Sonraki zil: Hesaplanıyor...")
                if hasattr(self, 'countdown_label'):
                    self.countdown_label.setText("Sonraki zil: Hesaplanıyor...")
            else:
                saat = int(fark.total_seconds() // 3600)
                dakika = int((fark.total_seconds() % 3600) // 60)
                saniye = int(fark.total_seconds() % 60)
                
                # Küçük geri sayım (saat yanında)
                if hasattr(self, 'countdown_small_label'):
                    self.countdown_small_label.setText(f"{saat:02d}")
                
                # Banner geri sayımı - Resimdeki formatta
                zil_tipi = sonraki_zil["type"]
                if zil_tipi == "ogrenci_giris":
                    tip_str = "Öğrenci Giriş"
                elif zil_tipi == "ogretmen_giris":
                    tip_str = "Öğretmen Giriş"
                else:
                    tip_str = "Ders Çıkış"
                
                if hasattr(self, 'countdown_banner_label'):
                    # Saniye bilgisini de ekle
                    if saat > 0:
                        self.countdown_banner_label.setText(
                            f"{sonraki_zil['lesson']}. Ders {tip_str} - {sonraki_zil['time'].strftime('%H:%M')} ({saat:02d}:{dakika:02d}:{saniye:02d} kaldı)"
                        )
                    elif dakika > 0:
                        self.countdown_banner_label.setText(
                            f"{sonraki_zil['lesson']}. Ders {tip_str} - {sonraki_zil['time'].strftime('%H:%M')} ({dakika:02d}:{saniye:02d} kaldı)"
                        )
                    else:
                        self.countdown_banner_label.setText(
                            f"{sonraki_zil['lesson']}. Ders {tip_str} - {sonraki_zil['time'].strftime('%H:%M')} ({saniye:02d} saniye kaldı)"
                        )
                
                # Sol paneldeki açıklama
                if hasattr(self, 'countdown_label'):
                    self.countdown_label.setText(
                        f"{sonraki_zil['lesson']}. Ders {tip_str} - {sonraki_zil['time'].strftime('%H:%M')}"
                    )
        else:
            if hasattr(self, 'countdown_small_label'):
                self.countdown_small_label.setText("--")
            if hasattr(self, 'countdown_banner_label'):
                self.countdown_banner_label.setText("Bugün için zil zamanı yok")
            if hasattr(self, 'countdown_label'):
                self.countdown_label.setText("Bugün için zil zamanı yok")
    
    def _update_today_schedule(self):
        """Bugünün ders programını tablo olarak göster - Resimdeki gibi: Ders, Giriş Zili, Öğretmen Zili, Çıkış Zili"""
        if not hasattr(self, 'today_schedule_table'):
            return
            
        simdi = datetime.now()
        simdiki_saat = simdi.time()
        gun_adi = self._get_day_name(simdi.weekday())
        
        schedule = self.scheduler.schedule_data
        if gun_adi not in schedule.get("days", {}):
            self.today_schedule_table.setRowCount(1)
            item = QTableWidgetItem("Bugün için program yok")
            item.setTextAlignment(Qt.AlignCenter)
            self.today_schedule_table.setItem(0, 0, item)
            self.today_schedule_table.setSpan(0, 0, 1, 4)
            return
        
        gun_data = schedule["days"][gun_adi]
        if not gun_data.get("active", False):
            self.today_schedule_table.setRowCount(1)
            item = QTableWidgetItem("Bugün zil yok (pasif gün)")
            item.setTextAlignment(Qt.AlignCenter)
            self.today_schedule_table.setItem(0, 0, item)
            self.today_schedule_table.setSpan(0, 0, 1, 4)
            return
        
        lessons = gun_data.get("lessons", [])
        if not lessons:
            self.today_schedule_table.setRowCount(1)
            item = QTableWidgetItem("Bugün için ders programı yok")
            item.setTextAlignment(Qt.AlignCenter)
            self.today_schedule_table.setItem(0, 0, item)
            self.today_schedule_table.setSpan(0, 0, 1, 4)
            return
        
        # Tabloyu doldur - Her ders için bir satır
        # Signal'ları blokla - güncelleme sırasında tıklama sorunlarını önle
        self.today_schedule_table.blockSignals(True)
        self.today_schedule_table.setRowCount(len(lessons))
        for row, ders in enumerate(lessons):
            ders_no = ders.get("lesson", 0)
            ogrenci_str = ders.get("ogrenci_giris", "")
            ogretmen_str = ders.get("ogretmen_giris", "")
            cikis_str = ders.get("ders_cikis", "")
            
            # Ders numarası
            ders_item = QTableWidgetItem(f"{ders_no}.Ders")
            ders_item.setTextAlignment(Qt.AlignCenter)
            
            # Giriş Zili
            giris_item = QTableWidgetItem(ogrenci_str)
            giris_item.setTextAlignment(Qt.AlignCenter)
            
            # Öğretmen Zili
            ogretmen_item = QTableWidgetItem(ogretmen_str)
            ogretmen_item.setTextAlignment(Qt.AlignCenter)
            
            # Çıkış Zili
            cikis_item = QTableWidgetItem(cikis_str)
            cikis_item.setTextAlignment(Qt.AlignCenter)
            
            # Çalmadan önce beyaz, çaldıktan sonra kırmızı
            try:
                cikis_saat = datetime.strptime(cikis_str, "%H:%M").time()
                if simdiki_saat >= cikis_saat:
                    # Ders bitti - kırmızı
                    ders_item.setForeground(QColor(200, 0, 0))
                    giris_item.setForeground(QColor(200, 0, 0))
                    ogretmen_item.setForeground(QColor(200, 0, 0))
                    cikis_item.setForeground(QColor(200, 0, 0))
                    ders_item.setBackground(QColor(255, 240, 240))
                    giris_item.setBackground(QColor(255, 240, 240))
                    ogretmen_item.setBackground(QColor(255, 240, 240))
                    cikis_item.setBackground(QColor(255, 240, 240))
                else:
                    # Ders devam ediyor veya bekliyor - beyaz
                    ders_item.setForeground(QColor(0, 0, 0))
                    giris_item.setForeground(QColor(0, 0, 0))
                    ogretmen_item.setForeground(QColor(0, 0, 0))
                    cikis_item.setForeground(QColor(0, 0, 0))
                    ders_item.setBackground(QColor(255, 255, 255))
                    giris_item.setBackground(QColor(255, 255, 255))
                    ogretmen_item.setBackground(QColor(255, 255, 255))
                    cikis_item.setBackground(QColor(255, 255, 255))
            except:
                pass
            
            self.today_schedule_table.setItem(row, 0, ders_item)
            self.today_schedule_table.setItem(row, 1, giris_item)
            self.today_schedule_table.setItem(row, 2, ogretmen_item)
            self.today_schedule_table.setItem(row, 3, cikis_item)
        
        # Signal'ları tekrar aç
        self.today_schedule_table.blockSignals(False)
        
        # Kolon genişliklerini ayarla
        self.today_schedule_table.resizeColumnsToContents()
        
        # Seçimi temizle - tıklama sorunlarını önle
        self.today_schedule_table.clearSelection()
    
    def _get_day_name(self, weekday: int) -> str:
        """Haftanın günü adını döndür"""
        gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        return gunler[weekday]
    
    def _update_status(self):
        """Durum etiketlerini güncelle"""
        durum = self.state_manager.durum
        mod = self.state_manager.mod
        
        if durum == ZilDurumu.ACIK:
            self.status_label.setText("Zil: AÇIK")
            self.status_label.setStyleSheet("color: #2e7d32; font-weight: bold; font-size: 13pt; padding: 0px;")
            self.btn_zil_ac_kapat.setText("Zili Kapat")
        else:
            self.status_label.setText("Zil: KAPALI")
            self.status_label.setStyleSheet("color: #c62828; font-weight: bold; font-size: 13pt; padding: 0px;")
            self.btn_zil_ac_kapat.setText("Zili Aç")
        
        mod_str = {
            ZilModu.NORMAL: "Normal",
            ZilModu.TATIL: "Tatil",
            ZilModu.SINAV: "Sınav"
        }[mod]
        self.mode_label.setText(f"Mod: {mod_str}")
        
        # Mod rengini ayarla
        if mod == ZilModu.NORMAL:
            self.mode_label.setStyleSheet("color: #1976d2; font-weight: bold; font-size: 13pt; padding: 0px;")
        elif mod == ZilModu.TATIL:
            self.mode_label.setStyleSheet("color: #f57c00; font-weight: bold; font-size: 13pt; padding: 0px;")
        else:  # SINAV
            self.mode_label.setStyleSheet("color: #7b1fa2; font-weight: bold; font-size: 13pt; padding: 0px;")
    
    def _on_zil_calindi(self, zil_tipi: str, aciklama: str, ses_dosyasi: str, anons_dosyasi: str = ""):
        """Otomatik zil çalındığında"""
        # Zil durumu kontrolü - eğer kapalıysa veya tatil modundaysa çalma
        if not self.state_manager.zil_calabilir_mi():
            self.logger.log_uyari(f"Zil çalınmadı (Durum: {self.state_manager.durum.value}, Mod: {self.state_manager.mod.value})")
            return
        
        # Ses seviyesini ayarla
        ses_seviyesi = 100
        settings = self._get_settings()
        volumes = settings.get("volumes", {})
        
        if zil_tipi == "ogrenci_giris":
            ses_seviyesi = volumes.get("ogrenci", 100)
        elif zil_tipi == "ogretmen_giris":
            ses_seviyesi = volumes.get("ogretmen", 100)
        elif zil_tipi == "ders_cikis":
            ses_seviyesi = volumes.get("ogrenci", 100)
        
        # Zil sesini çal
        if self.sound_player.play(ses_dosyasi, ses_seviyesi):
            self.logger.log_otomatik(f"{datetime.now().strftime('%H:%M')} {aciklama}")
            
            # Zil bittikten sonra anons çal
            if anons_dosyasi:
                def play_anons_after_zil():
                    # Zil bittikten sonra anons çal
                    if self.sound_player.play(anons_dosyasi, ses_seviyesi):
                        self.logger.log_otomatik(f"{datetime.now().strftime('%H:%M')} Anons çalındı: {anons_dosyasi}")
                
                # Zil bittiğinde anons çal
                self.sound_player.finished.connect(play_anons_after_zil)
        else:
            self.logger.log_hata(f"Ses dosyası bulunamadı: {ses_dosyasi}")
    
    def _play_ogrenci_manuel(self):
        """Manuel öğrenci zili çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        dosya = sounds.get("ogrenci", "ziller/zil1.mp3")
        ses_seviyesi = volumes.get("ogrenci", 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Öğrenci zili çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_ogretmen_manuel(self):
        """Manuel öğretmen zili çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        dosya = sounds.get("ogretmen", "ziller/zil1.mp3")
        ses_seviyesi = volumes.get("ogretmen", 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Öğretmen zili çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_cikis_manuel(self):
        """Manuel çıkış zili çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        dosya = sounds.get("cikis", "ziller/zil1.mp3")
        ses_seviyesi = volumes.get("cikis", 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Çıkış zili çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_manuel(self, tip: str, dosya: str):
        """Manuel zil çal (genel - diğer ziller için)"""
        settings = self._get_settings()
        volumes = settings.get("volumes", {})
        
        ses_seviyesi = volumes.get(tip, 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} {tip.upper()} zili çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_mars_manuel(self):
        """Manuel İstiklal Marşı çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        dosya = sounds.get("mars", "marslar/istiklal.mp3")
        ses_seviyesi = volumes.get("mars", 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} İstiklal Marşı çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_siren_manuel(self):
        """Manuel Siren çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        dosya = sounds.get("siren", "siren/siren.mp3")
        ses_seviyesi = volumes.get("siren", 100)
        
        if self.sound_player.play(dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Siren çalındı")
        else:
            QMessageBox.warning(self, "Hata", f"Ses dosyası bulunamadı:\n{dosya}")
    
    def _play_saygi_durusu(self):
        """Saygı duruşu + İstiklal Marşı çal"""
        # Önce mevcut sesi durdur ve tüm bağlantıları temizle
        self.sound_player.stop()
        # Tüm finished signal bağlantılarını temizle
        try:
            self.sound_player.finished.disconnect()
        except:
            pass
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        # Önce saygı duruşu (varsa)
        saygi = sounds.get("saygi", "")
        if saygi and saygi.strip():
            ses_seviyesi = volumes.get("mars", 100)
            if self.sound_player.play(saygi, ses_seviyesi):
                # Ses bittiğinde marşı çal
                def play_mars_after_saygi():
                    self.sound_player.finished.disconnect(play_mars_after_saygi)
                    mars_dosya = sounds.get("mars", "marslar/istiklal.mp3")
                    mars_seviyesi = volumes.get("mars", 100)
                    if self.sound_player.play(mars_dosya, mars_seviyesi):
                        self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} İstiklal Marşı çalındı")
                
                self.sound_player.finished.connect(play_mars_after_saygi)
                self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Saygı Duruşu başladı")
            else:
                # Saygı duruşu dosyası bulunamadı, direkt marşı çal
                mars_dosya = sounds.get("mars", "marslar/istiklal.mp3")
                mars_seviyesi = volumes.get("mars", 100)
                if self.sound_player.play(mars_dosya, mars_seviyesi):
                    self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} İstiklal Marşı çalındı")
        else:
            # Saygı duruşu yok, direkt marşı çal
            mars_dosya = sounds.get("mars", "marslar/istiklal.mp3")
            ses_seviyesi = volumes.get("mars", 100)
            if self.sound_player.play(mars_dosya, ses_seviyesi):
                self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Saygı Duruşu + İstiklal Marşı çalındı")
    
    def _play_siren_mars(self):
        """Siren + İstiklal Marşı çal"""
        # Önce mevcut sesi durdur
        self.sound_player.stop()
        
        settings = self._get_settings()
        sounds = settings.get("sounds", {})
        volumes = settings.get("volumes", {})
        
        # Önce siren (özel ses dosyası varsa onu kullan)
        siren_dosya = sounds.get("siren_mars_siren", sounds.get("siren", "siren/siren.mp3"))
        ses_seviyesi = volumes.get("siren", 100)
        
        if self.sound_player.play(siren_dosya, ses_seviyesi):
            self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Siren çalındı")
            
            # Siren bittiğinde marşı çal (özel ses dosyası varsa onu kullan)
            def play_mars_after_siren():
                self.sound_player.finished.disconnect(play_mars_after_siren)
                mars_dosya = sounds.get("siren_mars_mars", sounds.get("mars", "marslar/istiklal.mp3"))
                mars_seviyesi = volumes.get("mars", 100)
                if self.sound_player.play(mars_dosya, mars_seviyesi):
                    self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} İstiklal Marşı çalındı")
            
            self.sound_player.finished.connect(play_mars_after_siren)
        else:
            QMessageBox.warning(self, "Hata", f"Siren dosyası bulunamadı:\n{siren_dosya}")
    
    def _stop_sound(self):
        """Sesi durdur"""
        # Tüm finished signal bağlantılarını temizle
        try:
            self.sound_player.finished.disconnect()
        except:
            pass
        self.sound_player.stop()
        self.logger.log_manuel(f"{datetime.now().strftime('%H:%M')} Ses durduruldu")
    
    def _toggle_zil(self):
        """Zili aç/kapat"""
        if self.state_manager.durum == ZilDurumu.ACIK:
            # Zil kapatma seçenekleri
            from PySide6.QtWidgets import QInputDialog, QMessageBox
            from datetime import datetime, time
            
            items = ["Süresiz Kapat", "Belirli Saate Kadar Kapat", "İptal"]
            choice, ok = QInputDialog.getItem(
                self, "Zil Kapatma", "Nasıl kapatmak istersiniz?", items, 0, False
            )
            
            if not ok or choice == "İptal":
                return
            
            if choice == "Süresiz Kapat":
                self.state_manager.zil_kapat()
                self.scheduler.stop()
                self.logger.log_sistem("Zil süresiz kapatıldı")
            elif choice == "Belirli Saate Kadar Kapat":
                # Saat seç
                saat_str, ok = QInputDialog.getText(
                    self, "Zil Kapatma", 
                    "Hangi saate kadar kapatılsın? (HH:MM formatında, örn: 12:00):"
                )
                if ok and saat_str:
                    try:
                        saat, dakika = map(int, saat_str.split(":"))
                        kapatma_saati = time(saat, dakika)
                        # Geçici kapatma için state_manager'a ekle
                        self.state_manager._gecici_kapatma_saati = kapatma_saati
                        self.state_manager.zil_kapat()
                        self.scheduler.stop()
                        self.logger.log_sistem(f"Zil {saat_str} saatine kadar kapatıldı")
                    except:
                        QMessageBox.warning(self, "Hata", "Geçersiz saat formatı! HH:MM formatında girin.")
                        return
        else:
            self.state_manager.zil_ac()
            if hasattr(self.state_manager, '_gecici_kapatma_saati'):
                delattr(self.state_manager, '_gecici_kapatma_saati')
            self.scheduler.start()
            self.logger.log_sistem("Zil açıldı")
        
        self._update_status()
    
    def _show_schedule_editor(self):
        """Ders programı editörünü göster"""
        editor = ScheduleEditor(parent=self)
        if editor.exec():
            # Programı yeniden yükle
            self.scheduler._load_schedule()
            self._update_countdown()  # Geri sayımı güncelle
            self.logger.log_sistem("Ders programı güncellendi")
    
    def _show_settings(self):
        """Ayarlar penceresini göster"""
        settings_window = SettingsWindow(parent=self)
        if settings_window.exec():
            # Ayarları yeniden yükle
            self._load_settings()
            self.logger.log_sistem("Ayarlar güncellendi")
    
    def _load_settings(self):
        """Ayarları yükle"""
        settings = self._get_settings()
        
        # Modu ayarla
        mode_str = settings.get("mode", "normal")
        if mode_str == "tatil":
            self.state_manager.mod_degistir(ZilModu.TATIL)
        elif mode_str == "sinav":
            self.state_manager.mod_degistir(ZilModu.SINAV)
        else:
            self.state_manager.mod_degistir(ZilModu.NORMAL)
        
        self._update_status()
    
    def _get_settings(self) -> dict:
        """Ayarları oku"""
        # Çalışma dizinini bul (main.py'nin olduğu yer)
        base_dir = Path(__file__).parent.parent
        settings_file = base_dir / "data" / "settings.json"
        try:
            if settings_file.exists():
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def closeEvent(self, event):
        """Pencere kapatılırken"""
        # Sistem tepsisine küçültme ayarını kontrol et
        settings = self._get_settings()
        system = settings.get("system", {})
        tray_enabled = system.get("tray", True)
        
        if tray_enabled:
            # Sistem tepsisine küçült
            event.ignore()
            self.hide()
            self.logger.log_sistem("Pencere sistem tepsisine küçültüldü")
        else:
            # Normal kapatma
            self.scheduler.stop()
            self.sound_player.stop()
            self.logger.log_sistem("Uygulama kapatıldı")
            event.accept()
    
    def showEvent(self, event):
        """Pencere gösterildiğinde"""
        super().showEvent(event)
        # Tray menüsünü güncelle (eğer tray varsa)
        if hasattr(self, 'tray') and self.tray:
            if hasattr(self.tray, 'show_action') and hasattr(self.tray, 'hide_action'):
                self.tray.show_action.setEnabled(False)
                self.tray.hide_action.setEnabled(True)
    
    def hideEvent(self, event):
        """Pencere gizlendiğinde"""
        super().hideEvent(event)
        # Tray menüsünü güncelle (eğer tray varsa)
        if hasattr(self, 'tray') and self.tray:
            if hasattr(self.tray, 'show_action') and hasattr(self.tray, 'hide_action'):
                self.tray.show_action.setEnabled(True)
                self.tray.hide_action.setEnabled(False)

