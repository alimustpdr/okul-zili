"""
Durum yöneticisi - Zil durumu, modlar (tatil, sınav vb.)
"""
from enum import Enum
from typing import Optional


class ZilModu(Enum):
    """Zil çalışma modları"""
    NORMAL = "normal"
    TATIL = "tatil"
    SINAV = "sinav"


class ZilDurumu(Enum):
    """Zil durumu"""
    ACIK = "açık"
    KAPALI = "kapalı"


class StateManager:
    """Uygulama durum yöneticisi"""
    
    def __init__(self):
        self._durum = ZilDurumu.ACIK
        self._mod = ZilModu.NORMAL
        self._sifre_hash: Optional[str] = None
        self._gecici_kapatma_saati: Optional[time] = None
    
    @property
    def durum(self) -> ZilDurumu:
        """Mevcut zil durumunu döndür"""
        return self._durum
    
    @property
    def mod(self) -> ZilModu:
        """Mevcut zil modunu döndür"""
        return self._mod
    
    def zil_ac(self):
        """Zili aç"""
        self._durum = ZilDurumu.ACIK
    
    def zil_kapat(self):
        """Zili kapat"""
        self._durum = ZilDurumu.KAPALI
    
    def mod_degistir(self, yeni_mod: ZilModu):
        """Zil modunu değiştir"""
        self._mod = yeni_mod
    
    def zil_calabilir_mi(self) -> bool:
        """Zil çalabilir mi kontrolü"""
        if self._durum == ZilDurumu.KAPALI:
            # Geçici kapatma kontrolü
            if self._gecici_kapatma_saati:
                from datetime import datetime
                simdi = datetime.now().time()
                # Eğer geçici kapatma saati geçtiyse zili aç
                if simdi >= self._gecici_kapatma_saati:
                    self.zil_ac()
                    self._gecici_kapatma_saati = None
                    return True
            return False
        if self._mod == ZilModu.TATIL:
            return False
        return True
    
    def sifre_ayarla(self, sifre_hash: str):
        """Şifre hash'ini ayarla"""
        self._sifre_hash = sifre_hash
    
    def sifre_kontrol(self, sifre_hash: str) -> bool:
        """Şifre kontrolü"""
        if self._sifre_hash is None:
            return True  # Şifre ayarlanmamışsa geç
        return self._sifre_hash == sifre_hash

