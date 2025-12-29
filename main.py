"""
Okul Zil Programı - Ana Giriş Noktası
Windows 10+ için profesyonel okul zil sistemi
"""
import sys
from pathlib import Path

# Proje kök dizinini Python path'ine ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QDialog
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from ui.tray import TrayIcon
from core.logger import ZilLogger


def main():
    """Ana fonksiyon"""
    # Yüksek DPI desteği
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Tray icon için
    
    # Logger başlat
    logger = ZilLogger()
    
    try:
        # Ana pencere
        main_window = MainWindow()
        
        # Sistem tepsi ikonu - main_window referansını ver
        tray = TrayIcon(parent=main_window)
        tray.set_main_window(main_window)
        tray.show()
        
        # Ana pencereye tray referansını ver
        main_window.tray = tray
        
        # Tray sinyallerini bağla
        def show_main_window():
            main_window.show()
            main_window.raise_()
            main_window.activateWindow()
            main_window.setWindowState(main_window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        
        tray.show_window.connect(show_main_window)
        tray.quit_app.connect(app.quit)
        
        # İlk çalıştırmada pencereyi göster
        main_window.show()
        
        logger.log_sistem("Uygulama başarıyla başlatıldı")
        
        sys.exit(app.exec())
        
    except Exception as e:
        logger.log_hata(f"Kritik hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

