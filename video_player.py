# video_player.py
"""
Handler khusus pemutaran Video MP4 bersuara menggunakan ffpyplayer.
Solusi untuk OpenCV yang tidak mendukung playback audio bawaan.
"""
import cv2
from ffpyplayer.player import MediaPlayer


class MemeVideoPlayer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.player = MediaPlayer(video_path)
        self.is_playing = True

    def get_frame(self):
        """
        Mengambil frame video dan sinkronisasi audio secara real-time.
        """
        ret, frame = self.cap.read()
        audio_frame, val = self.player.get_frame()

        if not ret:
            self.is_playing = False
            self.cap.release()
            return None

        return frame

    def close(self):
        """Membersihkan resource video dan audio player."""
        self.is_playing = False
        self.cap.release()
        self.player.close_player()