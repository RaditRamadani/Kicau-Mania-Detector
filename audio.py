import threading
import time
import os
import sys

try:
    import pygame
    HAS_PYGAME = True
except ImportError:
    HAS_PYGAME = False

try:
    from playsound import playsound
    HAS_PLAYSOUND = True
except ImportError:
    HAS_PLAYSOUND = False


class AudioPlayer:
    """Simple audio player for kicau sound effects."""

    def __init__(self, audio_path: str = "kicau.mp3") -> None:
        self.audio_path = audio_path
        self.playing = False
        self._thread = None
        self._stop_event = threading.Event()

        # Try to initialize pygame mixer
        self._use_pygame = False
        if HAS_PYGAME:
            try:
                pygame.mixer.init()
                if os.path.exists(audio_path):
                    pygame.mixer.music.load(audio_path)
                    self._use_pygame = True
            except Exception:
                pass

    def play(self, loop: bool = True) -> None:
        if self.playing:
            return

        if not os.path.exists(self.audio_path):
            print(f"[INFO] Audio file '{self.audio_path}' not found, playing without sound.")
            return

        self.playing = True
        self._stop_event.clear()

        if self._use_pygame:
            try:
                pygame.mixer.music.load(self.audio_path)
                pygame.mixer.music.play(-1 if loop else 0)
            except Exception as e:
                print(f"[WARNING] Audio error: {e}")
        else:
            # Fallback: use playsound in thread
            if HAS_PLAYSOUND:
                self._thread = threading.Thread(target=self._play_thread, daemon=True)
                self._thread.start()
            else:
                # Last resort: try winsound on Windows
                if sys.platform == 'win32':
                    self._thread = threading.Thread(target=self._play_winsound, daemon=True)
                    self._thread.start()

    def stop(self) -> None:
        self.playing = False
        self._stop_event.set()

        if self._use_pygame:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def _play_thread(self) -> None:
        try:
            while not self._stop_event.is_set():
                playsound(self.audio_path, block=True)
        except Exception:
            pass

    def _play_winsound(self) -> None:
        try:
            import winsound
            while not self._stop_event.is_set():
                winsound.PlaySound(self.audio_path, winsound.SND_FILENAME)
        except Exception:
            pass

    def cleanup(self) -> None:
        self.stop()
        if self._use_pygame:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
