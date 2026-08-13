# meme_engine.py
"""
Core Engine untuk pemrosesan Computer Vision MediaPipe dan Logika Matematika Pose.
"""
import cv2
import numpy as np
import mediapipe as mp


class MemeEngine:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    @staticmethod
    def calculate_angle(a, b, c):
        """Menghitung sudut (derajat) antara 3 titik koordinat [x, y]"""
        a = np.array(a)
        b = np.array(b)  # Titik pusat sendi
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)

        if angle > 180.0:
            angle = 360.0 - angle

        return angle

    def process_frame(self, frame):
        """Mengonversi BGR ke RGB dan memproses frame via MediaPipe Pose"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        return results.pose_landmarks

    def check_jokowi_pose(self, landmarks):
        """Kondisi Trigger: Tangan diangkat melampaui posisi hidung/kepala"""
        if not landmarks:
            return False

        lm = landmarks.landmark
        nose_y = lm[self.mp_pose.PoseLandmark.NOSE].y
        left_wrist_y = lm[self.mp_pose.PoseLandmark.LEFT_WRIST].y
        right_wrist_y = lm[self.mp_pose.PoseLandmark.RIGHT_WRIST].y

        # Pada MediaPipe, koordinat Y = 0 berada di paling ATAS
        return left_wrist_y < nose_y or right_wrist_y < nose_y

    def check_spiderman_pose(self, landmarks):
        """Kondisi Trigger: Lengan terentang lurus (sudut siku mendekati 180 deg)"""
        if not landmarks:
            return False

        lm = landmarks.landmark

        # Landmark Lengan Kiri
        shoulder = [lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].x, lm[self.mp_pose.PoseLandmark.LEFT_SHOULDER].y]
        elbow = [lm[self.mp_pose.PoseLandmark.LEFT_ELBOW].x, lm[self.mp_pose.PoseLandmark.LEFT_ELBOW].y]
        wrist = [lm[self.mp_pose.PoseLandmark.LEFT_WRIST].x, lm[self.mp_pose.PoseLandmark.LEFT_WRIST].y]

        angle = self.calculate_angle(shoulder, elbow, wrist)
        return angle > 160.0