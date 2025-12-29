"""
Log sistemi - Tüm olayları logs/zil.log dosyasına yazar
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class ZilLogger:
    """Okul zil programı için log yöneticisi"""
    
    def __init__(self, log_dir: str = "logs"):
        # Çalışma dizinini bul (main.py'nin olduğu yer)
        base_dir = Path(__file__).parent.parent
        self.log_dir = base_dir / log_dir
        self.log_dir.mkdir(exist_ok=True)
        
        log_file = self.log_dir / "zil.log"
        
        # Log formatı: [TARIH SAAT] [SEVIYE] Mesaj
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()  # Konsola da yaz
            ]
        )
        
        self.logger = logging.getLogger('ZilProgrami')
    
    def log_otomatik(self, mesaj: str):
        """Otomatik zil çalma olaylarını logla"""
        self.logger.info(f"[OTOMATIK] {mesaj}")
    
    def log_manuel(self, mesaj: str):
        """Manuel zil çalma olaylarını logla"""
        self.logger.info(f"[MANUEL] {mesaj}")
    
    def log_sistem(self, mesaj: str):
        """Sistem olaylarını logla"""
        self.logger.info(f"[SISTEM] {mesaj}")
    
    def log_hata(self, mesaj: str):
        """Hata olaylarını logla"""
        self.logger.error(f"[HATA] {mesaj}")
    
    def log_uyari(self, mesaj: str):
        """Uyarı olaylarını logla"""
        self.logger.warning(f"[UYARI] {mesaj}")

