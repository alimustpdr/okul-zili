"""
Sistem tepsisinde ikon gösterimi
"""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PySide6.QtCore import Signal, Qt


class TrayIcon(QSystemTrayIcon):
    """Sistem tepsi ikonu"""
    
    show_window = Signal()
    quit_app = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = None
        
        # Profesyonel bir ikon oluştur
        icon = self._create_icon()
        self.setIcon(icon)
        
        # Menü oluştur
        self.menu = QMenu()
        
        self.show_action = QAction("Pencereyi Göster", self)
        self.show_action.triggered.connect(self._show_main_window)
        self.menu.addAction(self.show_action)
        
        self.hide_action = QAction("Pencereyi Gizle", self)
        self.hide_action.triggered.connect(self._hide_main_window)
        self.hide_action.setEnabled(False)  # Başlangıçta gizli
        self.menu.addAction(self.hide_action)
        
        self.menu.addSeparator()
        
        quit_action = QAction("Çıkış", self)
        quit_action.triggered.connect(self.quit_app.emit)
        self.menu.addAction(quit_action)
        
        self.setContextMenu(self.menu)
        
        # İkona tıklanınca - çift tıklamada göster, tek tıklamada menü göster
        self.activated.connect(self._on_activated)
    
    def set_main_window(self, main_window):
        """Ana pencere referansını ayarla"""
        self.main_window = main_window
    
    def _create_icon(self):
        """Profesyonel bir zil ikonu oluştur"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Şeffaf arka plan
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Zil şekli çiz (daha profesyonel bir çan)
        # Çan gövdesi
        painter.setBrush(QColor(70, 130, 180))  # Çelik mavisi
        painter.setPen(QColor(50, 100, 150))
        # Çan şekli için yuvarlak üst kısım
        painter.drawEllipse(6, 4, 20, 18)
        
        # Çan alt kısmı (açık kısım)
        painter.setBrush(QColor(100, 150, 200))
        painter.drawEllipse(8, 10, 16, 14)
        
        # Zil dili (çan içindeki top)
        painter.setBrush(QColor(200, 200, 200))
        painter.setPen(QColor(150, 150, 150))
        painter.drawEllipse(14, 18, 4, 4)
        
        # Zil askısı (üstteki halka)
        painter.setPen(QColor(100, 100, 100))
        painter.setBrush(QColor(120, 120, 120))
        painter.drawEllipse(14, 2, 4, 4)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _on_activated(self, reason):
        """İkona tıklanınca"""
        # Çift tıklamada pencereyi göster/gizle
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.main_window and self.main_window.isVisible():
                self._hide_main_window()
            else:
                self._show_main_window()
        # Tek tıklamada menü gösterilir (otomatik olarak context menu açılır)
    
    def _show_main_window(self):
        """Ana pencereyi göster"""
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.main_window.setWindowState(
                self.main_window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive
            )
            # Menüyü güncelle
            self.show_action.setEnabled(False)
            self.hide_action.setEnabled(True)
    
    def _hide_main_window(self):
        """Ana pencereyi gizle"""
        if self.main_window:
            self.main_window.hide()
            # Menüyü güncelle
            self.show_action.setEnabled(True)
            self.hide_action.setEnabled(False)

