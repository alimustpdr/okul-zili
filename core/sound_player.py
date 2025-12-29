"""
Ses oynatıcı - Thread-safe ses çalma/durdurma
"""
import os
from pathlib import Path
from threading import Lock
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtCore import QUrl, QObject, Signal


class SoundPlayer(QObject):
    """Thread-safe ses oynatıcı"""
    
    finished = Signal()  # Ses çalma bittiğinde
    
    def __init__(self, sounds_dir: str = "sounds"):
        super().__init__()
        # Çalışma dizinini bul (main.py'nin olduğu yer)
        base_dir = Path(__file__).parent.parent
        self.sounds_dir = base_dir / sounds_dir
        self.lock = Lock()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        # PySide6'da finished signal yok, playbackStateChanged kullanıyoruz
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self._is_playing = False
    
    def _on_playback_state_changed(self, state):
        """Oynatma durumu değiştiğinde çağrılır"""
        # QMediaPlayer.PlaybackState.StoppedState = 0
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self._is_playing:
                self._is_playing = False
                # Kısa bir gecikme sonra finished sinyalini gönder (anons için)
                from PySide6.QtCore import QTimer
                QTimer.singleShot(100, self.finished.emit)
    
    def play(self, dosya_adi: str, ses_seviyesi: int = 100) -> bool:
        """
        Ses dosyasını çal
        
        Args:
            dosya_adi: Ses dosyası adı (örn: "ziller/zil1.mp3" veya "sounds/ziller/zil1.mp3")
            ses_seviyesi: Ses seviyesi (0-100)
        
        Returns:
            Başarılı ise True
        """
        with self.lock:
            if self._is_playing:
                self.stop()
            
            # Dosya yolunu normalize et
            dosya_adi = dosya_adi.replace("\\", "/")
            
            # Mutlak yol mu kontrol et
            dosya_path_obj = Path(dosya_adi)
            if dosya_path_obj.is_absolute():
                # Mutlak yol ise direkt kullan
                dosya_yolu = dosya_path_obj
                if not dosya_yolu.exists():
                    return False
            else:
                # Relative yol - önce "sounds/" ile başlıyorsa kaldır
                if dosya_adi.startswith("sounds/"):
                    dosya_adi = dosya_adi[7:]  # "sounds/" kısmını kaldır
                
                # Önce sounds_dir ile birleştir
                dosya_yolu = self.sounds_dir / dosya_adi
                
                # Dosya yoksa alternatif yolları dene
                if not dosya_yolu.exists():
                    # Base directory'de dene
                    base_dir = Path(__file__).parent.parent
                    base_yol = base_dir / dosya_adi
                    if base_yol.exists():
                        dosya_yolu = base_yol
                    else:
                        # Son olarak "sounds/" ile başlayan yol olarak dene
                        sounds_yol = base_dir / "sounds" / dosya_adi
                        if sounds_yol.exists():
                            dosya_yolu = sounds_yol
                        else:
                            # Hala bulunamadıysa hata
                            return False
            
            # Ses seviyesini ayarla (0.0 - 1.0 arası)
            volume = max(0.0, min(1.0, ses_seviyesi / 100.0))
            self.audio_output.setVolume(volume)
            
            # Dosyayı çal
            url = QUrl.fromLocalFile(str(dosya_yolu.absolute()))
            self.player.setSource(url)
            self.player.play()
            self._is_playing = True
            
            return True
    
    def stop(self):
        """Sesi durdur"""
        with self.lock:
            if self._is_playing:
                self.player.stop()
                self._is_playing = False
    
    def is_playing(self) -> bool:
        """Şu anda ses çalıyor mu?"""
        with self.lock:
            return self._is_playing
    
    def set_volume(self, ses_seviyesi: int):
        """Ses seviyesini ayarla (0-100)"""
        volume = max(0.0, min(1.0, ses_seviyesi / 100.0))
        self.audio_output.setVolume(volume)

