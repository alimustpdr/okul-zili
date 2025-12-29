"""
Kurulum Sihirbazı - İlk Kullanım için Adım Adım Ayarlar
Ekran görüntülerine göre revize edilmiş versiyon
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QCheckBox, QComboBox, QTimeEdit, QRadioButton,
    QButtonGroup, QGroupBox, QLineEdit, QWidget, QStackedWidget,
    QMessageBox, QFrame, QGridLayout, QProgressDialog, QScrollArea
)
from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtGui import QFont, QKeyEvent


class SetupWizard(QDialog):
    """Kurulum sihirbazı - Adım adım ayar alma"""
    
    def __init__(self, schedule_file: str = "data/schedule.json", 
                 settings_file: str = "data/settings.json", parent=None):
        super().__init__(parent)
        base_dir = Path(__file__).parent.parent
        self.schedule_file = base_dir / schedule_file
        self.settings_file = base_dir / settings_file
        
        self.setWindowTitle("Okul Zili - Kurulum Sihirbazı")
        self.setMinimumSize(900, 600)
        self.setModal(True)
        
        # Veriler
        self.data = {
            "ders_suresi": 40,
            "sabah_ilk_ders": "08:30",
            "ogle_sonrasi_ilk_ders": "13:30",
            "ogle_tatili_ders_no": 4,
            "ogretmen_zili_var": True,
            "ogretmen_zili_fark": 2,
            "gunluk_ders_sayilari": {
                "Pazartesi": 8,
                "Salı": 8,
                "Çarşamba": 8,
                "Perşembe": 8,
                "Cuma": 8,
                "Cumartesi": 0,
                "Pazar": 0
            },
            "teneffus_sureleri": [10, 10, 10, 10, 10, 10]
        }
        
        self.gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        self.current_step = 0
        # Temel adımlar: ders_suresi, sabah, ogle_sonrasi, ogle_tatili, ogretmen_zili, ogretmen_fark (opsiyonel), günler, teneffüs, özet
        self.total_steps = 5 + len(self.gunler) + 2  # 5 temel + 7 gün + teneffüs + özet = 14
        
        # Widget referansları
        self.current_input_widget = None
        
        self._setup_ui()
    
    def keyPressEvent(self, event: QKeyEvent):
        """Enter tuşu ile ilerleme"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if self.current_step < self.total_steps - 1:
                self._next_step()
            elif self.current_step == self.total_steps - 1:
                self._finish()
        else:
            super().keyPressEvent(event)
    
    def _setup_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık
        title_label = QLabel("Okul Zili Kurulum Sihirbazı")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # İlerleme göstergesi
        self.progress_label = QLabel(f"Adım {self.current_step + 1} / {self.total_steps}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.progress_label)
        
        # Ana içerik alanı - İki panelli
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # Sol panel - Soru ve input
        self.left_panel = QWidget()
        self.left_panel.setMinimumWidth(500)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        self.question_label = QLabel()
        self.question_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #333;")
        self.question_label.setWordWrap(True)
        left_layout.addWidget(self.question_label)
        
        left_layout.addSpacing(30)
        
        # Input widget container
        self.input_container = QWidget()
        self.input_layout = QVBoxLayout()
        self.input_container.setLayout(self.input_layout)
        left_layout.addWidget(self.input_container)
        
        left_layout.addStretch()
        
        self.left_panel.setLayout(left_layout)
        main_layout.addWidget(self.left_panel)
        
        # Sağ panel - Açıklama kutusu
        self.right_panel = QFrame()
        self.right_panel.setMinimumWidth(300)
        self.right_panel.setMaximumWidth(350)
        self.right_panel.setStyleSheet("""
            QFrame {
                background-color: #ffebee;
                border: 2px solid #e57373;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(15, 15, 15, 15)
        
        # Logo/ikon alanı (isteğe bağlı)
        logo_label = QLabel("ℹ️")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 48px;")
        right_layout.addWidget(logo_label)
        
        self.help_label = QLabel()
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet("font-size: 13px; color: #c62828; line-height: 1.6;")
        self.help_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_layout.addWidget(self.help_label)
        
        right_layout.addStretch()
        
        self.right_panel.setLayout(right_layout)
        main_layout.addWidget(self.right_panel)
        
        layout.addLayout(main_layout)
        
        # Butonlar
        buttons_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("← Önceki")
        self.prev_btn.clicked.connect(self._prev_step)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setMinimumHeight(35)
        buttons_layout.addWidget(self.prev_btn)
        
        buttons_layout.addStretch()
        
        self.next_btn = QPushButton("Sonraki →")
        self.next_btn.clicked.connect(self._next_step)
        self.next_btn.setDefault(True)
        self.next_btn.setMinimumHeight(35)
        self.next_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        buttons_layout.addWidget(self.next_btn)
        
        self.finish_btn = QPushButton("Programı Oluştur ✓")
        self.finish_btn.clicked.connect(self._finish)
        self.finish_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        self.finish_btn.setVisible(False)
        self.finish_btn.setMinimumHeight(35)
        buttons_layout.addWidget(self.finish_btn)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # İlk adımı göster
        self._show_step(0)
    
    def _clear_layout(self, layout):
        """Layout içindeki tüm widget'ları temizle"""
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())
    
    def _show_step(self, step: int):
        """Belirtilen adımı göster"""
        self.current_step = step
        self.progress_label.setText(f"Adım {self.current_step + 1} / {self.total_steps}")
        
        # Önceki input widget'ı temizle - Daha kapsamlı temizlik
        # Önce tüm widget'ları kaldır
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setParent(None)
                widget.deleteLater()
            elif item.layout():
                # Layout varsa içindeki widget'ları da temizle
                self._clear_layout(item.layout())
        
        # Widget referansını sıfırla
        self.current_input_widget = None
        
        # UI güncellemesi için
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Soru ve açıklamayı ayarla
        if step == 0:
            self._setup_step_ders_suresi()
        elif step == 1:
            self._setup_step_sabah_ilk_ders()
        elif step == 2:
            self._setup_step_ogle_sonrasi()
        elif step == 3:
            self._setup_step_ogle_tatili()
        elif step == 4:
            self._setup_step_ogretmen_zili()
        elif step == 5:
            # Öğretmen zili varsa fark adımı, yoksa ilk gün adımı
            if self.data["ogretmen_zili_var"]:
                self._setup_step_ogretmen_fark()
            else:
                # Öğretmen zili yoksa bu adımı atla, ilk güne geç
                self._setup_step_gun_ders_sayisi(0)
        elif step >= 5 and step < 5 + len(self.gunler):
            # Öğretmen zili varsa: step 5 = fark, step 6-12 = günler
            # Öğretmen zili yoksa: step 5-11 = günler
            if self.data["ogretmen_zili_var"]:
                gun_index = step - 6
            else:
                gun_index = step - 5
            self._setup_step_gun_ders_sayisi(gun_index)
        elif step == 5 + len(self.gunler) if not self.data["ogretmen_zili_var"] else step == 6 + len(self.gunler):
            self._setup_step_teneffus()
        else:
            self._setup_step_summary()
        
        # Buton durumlarını güncelle
        self.prev_btn.setEnabled(step > 0)
        if step == self.total_steps - 1:
            self.next_btn.setVisible(False)
            self.finish_btn.setVisible(True)
            self.finish_btn.setDefault(True)
        else:
            self.next_btn.setVisible(True)
            self.finish_btn.setVisible(False)
            self.next_btn.setDefault(True)
    
    def _setup_step_ders_suresi(self):
        """Adım 0: Ders Süresi"""
        self.question_label.setText("Okulunuzdaki ders süresi :")
        self.help_label.setText(
            "Okulunuzda bir dersin kaç dakika sürdüğünü yazın.\n\n"
            "Genellikle 40 dakika olarak ayarlanır.\n"
            "20-60 dakika arası bir değer girebilirsiniz."
        )
        
        spin = QSpinBox()
        spin.setMinimum(20)
        spin.setMaximum(60)
        spin.setValue(self.data["ders_suresi"])
        spin.setSuffix(" dakika")
        spin.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        spin.valueChanged.connect(lambda v: self.data.update({"ders_suresi": v}))
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(spin)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = spin
    
    def _setup_step_sabah_ilk_ders(self):
        """Adım 1: Sabah İlk Ders"""
        self.question_label.setText("Sabah ilk derse başlama saati :")
        self.help_label.setText(
            "Sabah ilk dersin başlama saatini girin.\n\n"
            "Örnek: 08:30\n"
            "Bu saat, öğrenci giriş zilinin çalacağı saattir."
        )
        
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime.fromString(self.data["sabah_ilk_ders"], "HH:mm"))
        time_edit.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        time_edit.timeChanged.connect(lambda t: self.data.update({"sabah_ilk_ders": t.toString("HH:mm")}))
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(time_edit)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = time_edit
    
    def _setup_step_ogle_sonrasi(self):
        """Adım 2: Öğleden Sonra İlk Ders"""
        self.question_label.setText("Öğleden sonra ilk derse başlama saati :")
        self.help_label.setText(
            "Öğle tatilinden sonra ilk dersin başlama saatini girin.\n\n"
            "Örnek: 13:30\n"
            "Bu saat, öğle arasından sonraki ilk dersin başlangıç saatidir."
        )
        
        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime.fromString(self.data["ogle_sonrasi_ilk_ders"], "HH:mm"))
        time_edit.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        time_edit.timeChanged.connect(lambda t: self.data.update({"ogle_sonrasi_ilk_ders": t.toString("HH:mm")}))
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(time_edit)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = time_edit
    
    def _setup_step_ogle_tatili(self):
        """Adım 3: Öğle Tatili"""
        self.question_label.setText("Öğle tatili kaçıncı dersten sonra başlıyor? :")
        self.help_label.setText(
            "Öğle tatilinin kaçıncı dersten sonra başladığını belirtin.\n\n"
            "Örnek: 4. dersten sonra\n"
            "Genellikle 4. veya 5. dersten sonra öğle tatili yapılır."
        )
        
        spin = QSpinBox()
        spin.setMinimum(1)
        spin.setMaximum(8)
        spin.setValue(self.data["ogle_tatili_ders_no"])
        spin.setSuffix(". dersten sonra")
        spin.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        spin.valueChanged.connect(lambda v: self.data.update({"ogle_tatili_ders_no": v}))
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(spin)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = spin
    
    def _setup_step_ogretmen_zili(self):
        """Adım 4: Öğretmen Zili"""
        self.question_label.setText("Okulunuzda öğretmen zili kullanılıyor mu? :")
        self.help_label.setText(
            "Okulunuzda öğretmenler için ayrı bir zil çalıyor mu?\n\n"
            "Eğer öğretmen zili kullanılıyorsa, öğrenci zilinden sonra "
            "öğretmen zili çalar ve ders başlar."
        )
        
        group = QButtonGroup()
        
        evet_radio = QRadioButton("Evet")
        evet_radio.setChecked(self.data["ogretmen_zili_var"])
        evet_radio.setStyleSheet("font-size: 16px; padding: 10px;")
        
        hayir_radio = QRadioButton("Hayır")
        hayir_radio.setChecked(not self.data["ogretmen_zili_var"])
        hayir_radio.setStyleSheet("font-size: 16px; padding: 10px;")
        
        group.addButton(evet_radio, 1)
        group.addButton(hayir_radio, 0)
        
        evet_radio.toggled.connect(lambda checked: self.data.update({"ogretmen_zili_var": checked}) if checked else None)
        hayir_radio.toggled.connect(lambda checked: self.data.update({"ogretmen_zili_var": not checked}) if checked else None)
        
        radio_layout = QHBoxLayout()
        radio_layout.addStretch()
        radio_layout.addWidget(evet_radio)
        radio_layout.addSpacing(30)
        radio_layout.addWidget(hayir_radio)
        radio_layout.addStretch()
        
        self.input_layout.addLayout(radio_layout)
        self.current_input_widget = group
    
    def _setup_step_ogretmen_fark(self):
        """Adım 5: Öğretmen Zili Farkı"""
        if not self.data["ogretmen_zili_var"]:
            # Öğretmen zili yoksa bu adımı atla
            self._next_step()
            return
        
        self.question_label.setText("Öğretmen zili giriş zilinden kaç dakika sonra çalacak? :")
        self.help_label.setText(
            "Öğrenci giriş zilinden kaç dakika sonra öğretmen zilinin çalacağını belirtin.\n\n"
            "Örnek: 2 dakika\n"
            "Öğrenci zili 08:30'da çalarsa, öğretmen zili 08:32'de çalar."
        )
        
        spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(10)
        spin.setValue(self.data["ogretmen_zili_fark"])
        spin.setSuffix(" dakika")
        spin.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        spin.valueChanged.connect(lambda v: self.data.update({"ogretmen_zili_fark": v}))
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addWidget(spin)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = spin
    
    def _setup_step_gun_ders_sayisi(self, gun_index: int):
        """Adım 6-12: Günlük Ders Sayıları"""
        gun = self.gunler[gun_index]
        self.question_label.setText(f"{gun} günü ders sayısını belirtin :")
        self.help_label.setText(
            f"{gun} günü okulunuzda kaç ders işleniyor?\n\n"
            "Eğer o gün ders yoksa, '0' yazabilir veya "
            "sağdaki 'Ders yok' seçeneğini işaretleyebilirsiniz."
        )
        
        spin = QSpinBox()
        spin.setMinimum(0)
        spin.setMaximum(12)
        spin.setValue(self.data["gunluk_ders_sayilari"][gun])
        spin.setSuffix(" ders")
        spin.setStyleSheet("font-size: 18px; padding: 12px; min-width: 200px;")
        
        check = QCheckBox(f"{gun} ders yok.")
        check.setChecked(self.data["gunluk_ders_sayilari"][gun] == 0)
        check.setStyleSheet("font-size: 14px; padding: 10px;")
        
        def on_check_toggled(checked):
            if checked:
                spin.setValue(0)
                spin.setEnabled(False)
                self.data["gunluk_ders_sayilari"][gun] = 0
            else:
                spin.setEnabled(True)
                if spin.value() == 0:
                    spin.setValue(8)
                    self.data["gunluk_ders_sayilari"][gun] = 8
        
        def on_spin_changed(value):
            if value == 0:
                check.setChecked(True)
            else:
                check.setChecked(False)
            self.data["gunluk_ders_sayilari"][gun] = value
        
        check.toggled.connect(on_check_toggled)
        spin.valueChanged.connect(on_spin_changed)
        
        center_layout = QVBoxLayout()
        center_layout.addStretch()
        
        spin_layout = QHBoxLayout()
        spin_layout.addStretch()
        spin_layout.addWidget(spin)
        spin_layout.addStretch()
        center_layout.addLayout(spin_layout)
        
        center_layout.addSpacing(15)
        
        check_layout = QHBoxLayout()
        check_layout.addStretch()
        check_layout.addWidget(check)
        check_layout.addStretch()
        center_layout.addLayout(check_layout)
        
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = spin
    
    def _setup_step_teneffus(self):
        """Adım 13: Teneffüs Süreleri"""
        self.question_label.setText("Son olarak teneffüs sürelerini dakika olarak yazın :")
        self.help_label.setText(
            "Her teneffüsün kaç dakika süreceğini belirtin.\n\n"
            "Öğle arası hariç tüm teneffüsler için süre girin.\n"
            "Öğle arası süresi, öğleden sonra ilk ders saatinden otomatik hesaplanır."
        )
        
        grid = QGridLayout()
        grid.setSpacing(15)
        
        self.teneffus_spins = []
        for i in range(6):
            label = QLabel(f"{i+1}. Teneffüs s:")
            label.setStyleSheet("font-size: 14px;")
            
            spin = QSpinBox()
            spin.setMinimum(1)
            spin.setMaximum(60)
            if i < len(self.data["teneffus_sureleri"]):
                spin.setValue(self.data["teneffus_sureleri"][i])
            else:
                spin.setValue(10)
            spin.setSuffix(" dk")
            spin.setStyleSheet("font-size: 16px; padding: 8px; min-width: 120px;")
            
            row = i // 3
            col = (i % 3) * 2
            grid.addWidget(label, row, col)
            grid.addWidget(spin, row, col + 1)
            
            self.teneffus_spins.append(spin)
        
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(grid)
        center_layout.addStretch()
        
        self.input_layout.addLayout(center_layout)
        self.current_input_widget = self.teneffus_spins[0]
    
    def _setup_step_summary(self):
        """Son adım: Özet"""
        self.question_label.setText("Ayarlarınızın Özeti")
        self.help_label.setText(
            "Tüm ayarlarınızı kontrol edin.\n\n"
            "Eğer bir değişiklik yapmak isterseniz 'Önceki' butonuna basarak geri dönebilirsiniz.\n"
            "Her şey tamamsa 'Programı Oluştur' butonuna basın."
        )
        
        summary_text = f"""
        <div style='font-size: 14px; line-height: 1.8;'>
        <b>Ders Süresi:</b> {self.data['ders_suresi']} dakika<br>
        <b>Sabah İlk Ders:</b> {self.data['sabah_ilk_ders']}<br>
        <b>Öğleden Sonra İlk Ders:</b> {self.data['ogle_sonrasi_ilk_ders']}<br>
        <b>Öğle Tatili:</b> {self.data['ogle_tatili_ders_no']}. dersten sonra<br>
        <b>Öğretmen Zili:</b> {'Evet' if self.data['ogretmen_zili_var'] else 'Hayır'}<br>
        """
        
        if self.data['ogretmen_zili_var']:
            summary_text += f"<b>Öğretmen Zili Farkı:</b> {self.data['ogretmen_zili_fark']} dakika<br>"
        
        summary_text += "<br><b>Günlük Ders Sayıları:</b><br>"
        for gun, sayi in self.data['gunluk_ders_sayilari'].items():
            if sayi > 0:
                summary_text += f"  • {gun}: {sayi} ders<br>"
        
        summary_text += "<br><b>Teneffüs Süreleri:</b><br>"
        if hasattr(self, 'teneffus_spins') and self.teneffus_spins:
            for i, spin in enumerate(self.teneffus_spins, 1):
                summary_text += f"  • {i}. Teneffüs: {spin.value()} dakika<br>"
        else:
            # Teneffüs verilerini data'dan al
            for i, sure in enumerate(self.data.get("teneffus_sureleri", [10]*6), 1):
                summary_text += f"  • {i}. Teneffüs: {sure} dakika<br>"
        
        summary_text += "</div>"
        
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("""
            font-size: 13px;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 8px;
            border: 1px solid #ddd;
        """)
        summary_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Scroll area ekle (uzun özetler için)
        scroll_area = QScrollArea()
        scroll_area.setWidget(summary_label)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(scroll_area)
        
        self.input_layout.addLayout(scroll_layout)
    
    def _next_step(self):
        """Sonraki adıma geç"""
        # Mevcut adımın verilerini kaydet
        teneffus_step = 5 + len(self.gunler) if not self.data["ogretmen_zili_var"] else 6 + len(self.gunler)
        if self.current_step == teneffus_step and hasattr(self, 'teneffus_spins'):
            self.data["teneffus_sureleri"] = [spin.value() for spin in self.teneffus_spins]
        
        if self.current_step < self.total_steps - 1:
            next_step = self.current_step + 1
            
            # Öğretmen zili yoksa fark adımını atla
            if next_step == 5 and not self.data["ogretmen_zili_var"]:
                next_step = 6
            
            self._show_step(next_step)
    
    def _prev_step(self):
        """Önceki adıma dön"""
        if self.current_step > 0:
            prev_step = self.current_step - 1
            
            # Öğretmen zili yoksa fark adımını atla
            if prev_step == 5 and not self.data["ogretmen_zili_var"]:
                prev_step = 4
            
            # Eğer öğretmen zili yoksa ve prev_step 5 ise (ilk gün adımı), 4'e dön
            if prev_step == 5 and not self.data["ogretmen_zili_var"]:
                prev_step = 4
            
            self._show_step(prev_step)
    
    def _finish(self):
        """Sihirbazı tamamla ve programı oluştur"""
        # Teneffüs verilerini kaydet
        if hasattr(self, 'teneffus_spins'):
            self.data["teneffus_sureleri"] = [spin.value() for spin in self.teneffus_spins]
        
        # İlerleme penceresi oluştur
        progress = QProgressDialog("Ayarlar kaydediliyor...", None, 0, len(self.gunler) + 1, self)
        progress.setWindowTitle("Program Oluşturuluyor")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setCancelButton(None)  # İptal butonunu kaldır
        progress.setValue(0)
        
        # UI güncellemesi için
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()
        
        # Ayarları kaydet
        progress.setLabelText("Ayarlar kaydediliyor...")
        progress.setValue(0)
        QApplication.processEvents()
        
        settings_data = {
            "volumes": {
                "ogrenci": 100,
                "ogretmen": 100,
                "mars": 100,
                "siren": 100
            },
            "system": {
                "startup": True,
                "tray": True
            },
            "security": {
                "password_hash": None
            },
            "mode": "normal",
            "schedule_defaults": {
                "ilk_ders_baslangic": self.data["sabah_ilk_ders"],
                "standart_teneffus": self.data["teneffus_sureleri"][0] if self.data["teneffus_sureleri"] else 10,
                "gunluk_ders_sayisi": max(self.data["gunluk_ders_sayilari"].values()) if any(self.data["gunluk_ders_sayilari"].values()) else 8,
                "ogle_arasi_suresi": 40,  # Varsayılan
                "ogle_arasi_ders_no": self.data["ogle_tatili_ders_no"],
                "standart_ders_suresi": self.data["ders_suresi"],
                "ogrenci_giris_farki": self.data["ogretmen_zili_fark"] if self.data["ogretmen_zili_var"] else 0
            }
        }
        
        try:
            if not self.settings_file.parent.exists():
                self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            progress.close()
            QMessageBox.warning(self, "Hata", f"Ayarlar kaydedilemedi: {str(e)}")
            return
        
        # Program oluştur
        schedule_data = {"days": {}}
        progress.setValue(1)
        QApplication.processEvents()
        
        for gun_index, gun in enumerate(self.gunler):
            progress.setLabelText(f"Günler oluşturuluyor: {gun}")
            progress.setValue(gun_index + 1)
            QApplication.processEvents()
            
            ders_sayisi = self.data["gunluk_ders_sayilari"][gun]
            if ders_sayisi == 0:
                schedule_data["days"][gun] = {"active": False, "lessons": []}
                continue
            
            lessons = []
            ilk_ders_baslangic = datetime.strptime(self.data["sabah_ilk_ders"], "%H:%M")
            ogrenci_farki = self.data["ogretmen_zili_fark"] if self.data["ogretmen_zili_var"] else 0
            ders_suresi = self.data["ders_suresi"]
            ogle_ders_no = self.data["ogle_tatili_ders_no"]
            
            current_time = ilk_ders_baslangic
            teneffus_index = 0
            
            for ders_no in range(1, ders_sayisi + 1):
                # Öğle arası kontrolü - öğleden sonraki ilk ders için zamanı ayarla
                if ders_no == ogle_ders_no + 1:
                    current_time = datetime.strptime(self.data["ogle_sonrasi_ilk_ders"], "%H:%M")
                
                # Öğrenci girişi (öğretmen girişinden önce)
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
                if ders_no < ders_sayisi:
                    if ders_no == ogle_ders_no:
                        # Öğle arası - öğleden sonraki ilk ders saatinden hesapla
                        ogle_sonrasi = datetime.strptime(self.data["ogle_sonrasi_ilk_ders"], "%H:%M")
                        teneffus_suresi = int((ogle_sonrasi - ders_cikis).total_seconds() / 60)
                        # Negatif değer kontrolü
                        if teneffus_suresi < 0:
                            # Eğer öğle arası negatif çıkarsa, varsayılan değer kullan
                            teneffus_suresi = 40
                        # Öğle arasından sonra teneffus_index'i sıfırlama, devam et
                    else:
                        # Normal teneffüs
                        if teneffus_index < len(self.data["teneffus_sureleri"]):
                            teneffus_suresi = self.data["teneffus_sureleri"][teneffus_index]
                            teneffus_index += 1
                        else:
                            # Teneffüs dizisi yetersizse son değeri kullan
                            teneffus_suresi = self.data["teneffus_sureleri"][-1] if self.data["teneffus_sureleri"] else 10
                    
                    current_time = ders_cikis + timedelta(minutes=teneffus_suresi)
            
            schedule_data["days"][gun] = {
                "active": True,
                "lessons": lessons
            }
        
        progress.setLabelText("Program kaydediliyor...")
        progress.setValue(len(self.gunler) + 1)
        QApplication.processEvents()
        
        # Programı kaydet
        try:
            if not self.schedule_file.parent.exists():
                self.schedule_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            progress.close()
            QMessageBox.warning(self, "Hata", f"Program kaydedilemedi: {str(e)}")
            return
        
        progress.close()
        
        # Eğer parent bir ScheduleEditor ise, verileri otomatik yükle
        if self.parent() and hasattr(self.parent(), '_load_schedule') and hasattr(self.parent(), '_load_settings'):
            try:
                # Schedule editor'de verileri yeniden yükle
                self.parent()._load_schedule()
                self.parent()._load_settings()
                # Tablo editörü sekmesine geç ve ilk günü yükle
                if hasattr(self.parent(), '_load_day_to_table'):
                    self.parent()._load_day_to_table()
                QMessageBox.information(self, "Başarılı", 
                                      "Kurulum tamamlandı!\n"
                                      "Program oluşturuldu ve ayarlar kaydedildi.\n"
                                      "Ders programı tablosu güncellendi.")
            except Exception as e:
                QMessageBox.warning(self, "Uyarı", 
                                  f"Kurulum tamamlandı ancak tablo güncellenirken hata oluştu:\n{str(e)}")
        else:
            QMessageBox.information(self, "Başarılı", 
                                  "Kurulum tamamlandı!\nProgram oluşturuldu ve ayarlar kaydedildi.")
        
        self.accept()
