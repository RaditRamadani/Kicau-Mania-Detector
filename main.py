"""
🐦 Kicau Mania Detector
Deteksi gesture kicau: Tangan di mulut + Lambaikan tangan.
Musik dan GIF hanya menyala SAAT tangan bergerak. Kucing 4 di sudut.
"""
import time, sys, os
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass
import cv2
import numpy as np
import mediapipe as mp

from motion import WaveMotionTracker
from ui import GifPlayer
from audio import AudioPlayer

CAMERA_INDEX = 0
CAMERA_W, CAMERA_H = 1280, 720
MOUTH_THRESHOLD = 60
GIF_FILE = "cat_dance.gif"
AUDIO_FILE = "ssstik.io_1782872971130.mp3"

mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_mesh

class KicauDetector:
    def __init__(self):
        self.state = "IDLE"
        self.wave = WaveMotionTracker(
            window_seconds=1.0, min_speed=30.0,
            min_dir_changes=1, min_move_px=5.0,
            min_horizontal_ratio=0.1
        )
        self.gif = GifPlayer(GIF_FILE)
        self.audio = AudioPlayer(AUDIO_FILE)
        
        self.hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.5)
        self.face = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    def process(self, frame):
        now = time.time()
        h, w = frame.shape[:2]
        frame = cv2.flip(frame, 1)
        
        # Kamera bersih (hapus semua teks dan garis)
        clean_frame = frame.copy()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        hr = self.hands.process(rgb)
        fr = self.face.process(rgb)

        mouth = None
        if fr.multi_face_landmarks:
            fl = fr.multi_face_landmarks[0]
            mouth = (int((fl.landmark[13].x + fl.landmark[14].x)/2*w), 
                     int((fl.landmark[13].y + fl.landmark[14].y)/2*h))

        L = None
        R = None
        if hr.multi_hand_landmarks:
            for i, hl in enumerate(hr.multi_hand_landmarks):
                label = hr.multi_handedness[i].classification[0].label
                palm = (int(hl.landmark[9].x*w), int(hl.landmark[9].y*h))
                wrist = (int(hl.landmark[0].x*w), int(hl.landmark[0].y*h))
                if label == "Right":  # Flipped
                    L = {"palm": palm, "wrist": wrist}
                else:
                    R = {"palm": palm, "wrist": wrist}

        # STATE MACHINE
        hand_on_mouth = False
        if L and mouth:
            px, py = L["palm"]
            mx, my = mouth
            if ((px-mx)**2 + (py-my)**2)**0.5 < MOUTH_THRESHOLD * 1.5:
                hand_on_mouth = True
        
        is_trigger_active = False

        if not hand_on_mouth:
            self.wave = WaveMotionTracker(
                window_seconds=1.0, min_speed=30.0,
                min_dir_changes=1, min_move_px=5.0,
                min_horizontal_ratio=0.1
            ) # Reset lambaian jika tangan lepas dari mulut
        elif R:
            # Cek lambaian tangan kanan
            wx, wy = R["wrist"]
            wr = self.wave.update(wx, wy, now)
            if wr.is_waving:
                is_trigger_active = True

        if is_trigger_active:
            if self.state != "TRIGGERED":
                print("\n🐦🐦🐦 KICAU MANIA DETECTED! 🐦🐦🐦\n")
                self.state = "TRIGGERED"
                self.gif.start(now)
                self.audio.play(loop=True)

            # Terus putar musik dan GIF HANYA SELAMA TANGAN BERGERAK
            if self.gif.loaded:
                gif_frame = self.gif.get_frame(now)
                if gif_frame is not None:
                    # 4 Kucing di samping/sudut
                    small_cat = cv2.resize(gif_frame, (280, 280))
                    
                    # Hapus background hijau (Chroma Key)
                    hsv = cv2.cvtColor(small_cat, cv2.COLOR_BGR2HSV)
                    lower_green = np.array([30, 30, 30])
                    upper_green = np.array([90, 255, 255])
                    mask = cv2.inRange(hsv, lower_green, upper_green)
                    mask_inv = cv2.bitwise_not(mask)
                    
                    cat_fg = cv2.bitwise_and(small_cat, small_cat, mask=mask_inv)
                    
                    sh, sw = small_cat.shape[:2]
                    
                    # Posisi di 4 sudut layar
                    positions = [
                        (10, 10),                       # Kiri atas
                        (w - sw - 10, 10),              # Kanan atas
                        (10, h - sh - 20),              # Kiri bawah
                        (w - sw - 10, h - sh - 20)      # Kanan bawah
                    ]
                    
                    for px, py in positions:
                        if py + sh <= h and px + sw <= w and py >= 0 and px >= 0:
                            roi = clean_frame[py:py+sh, px:px+sw]
                            roi_bg = cv2.bitwise_and(roi, roi, mask=mask)
                            clean_frame[py:py+sh, px:px+sw] = cv2.add(roi_bg, cat_fg)
        else:
            # Jika berhenti gerak / tangan lepas, MATIKAN MUSIK & GIF
            if self.state == "TRIGGERED":
                print("\n[INFO] Berhenti bergerak. Musik dimatikan.\n")
                self.state = "IDLE"
                self.gif.stop()
                self.audio.stop()

        return clean_frame

    def cleanup(self):
        self.hands.close()
        self.face.close()
        self.audio.cleanup()

def main():
    det = KicauDetector()
    cap = cv2.VideoCapture(CAMERA_INDEX)
    # Biarkan kamera menggunakan resolusi bawaannya agar tidak gepeng

    if not cap.isOpened():
        print("[ERROR] Kamera tidak ditemukan!")
        sys.exit(1)

    cv2.namedWindow("Kicau Mania Detector", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setWindowProperty("Kicau Mania Detector", cv2.WND_PROP_TOPMOST, 1)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            result = det.process(frame)
            cv2.imshow("Kicau Mania Detector", result)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except KeyboardInterrupt:
        pass
    finally:
        det.cleanup()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
