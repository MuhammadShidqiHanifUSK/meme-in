# gui_app.py
"""
Antarmuka Desktop GUI Modern berbasis CustomTkinter.
Mengintegrasikan Live Camera Feed, Panel Kontrol, dan Monitor System.
"""
import time
import cv2
from PIL import Image, ImageTk
import customtkinter as ctk

from config import MEME_REGISTRY
from meme_engine import MemeEngine
from video_player import MemeVideoPlayer
from overlay_utils import overlay_transparent

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class MemeifyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Meme-ify Me - Dashboard Control Panel")
        self.geometry("1100x680")

        # System Components
        self.cap = cv2.VideoCapture(0)
        self.engine = MemeEngine()
        self.active_video = None
        self.spiderman_img = cv2.imread(MEME_REGISTRY["spiderman"]["path"], cv2.IMREAD_UNCHANGED)

        # FPS Tracker
        self.prev_time = time.time()

        # Build UI Layout
        self._setup_ui()

        # Start Video Loop
        self.update_feed()

    def _setup_ui(self):
        # Configure Grid Layout (1 row, 2 columns)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL: CAMERA DISPLAY ---
        self.cam_frame = ctk.CTkFrame(self, corner_radius=15)
        self.cam_frame.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        self.video_label = ctk.CTkLabel(self.cam_frame, text="")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # --- RIGHT PANEL: CONTROL PANEL ---
        self.control_frame = ctk.CTkFrame(self, corner_radius=15)
        self.control_frame.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")

        # Title Header
        self.title_label = ctk.CTkLabel(
            self.control_frame,
            text="⚙️ Control Panel",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(padx=20, pady=(20, 10), anchor="w")

        # Meme Toggles Section
        self.toggle_group = ctk.CTkFrame(self.control_frame)
        self.toggle_group.pack(padx=15, pady=10, fill="x")

        self.lbl_toggles = ctk.CTkLabel(
            self.toggle_group,
            text="Active Meme Detection:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_toggles.pack(padx=10, pady=5, anchor="w")

        self.switch_jokowi = ctk.CTkSwitch(self.toggle_group, text="Jokowi Berjuang (MP4)")
        self.switch_jokowi.select()
        self.switch_jokowi.pack(padx=10, pady=5, anchor="w")

        self.switch_spiderman = ctk.CTkSwitch(self.toggle_group, text="Spiderman Pointing (PNG)")
        self.switch_spiderman.select()
        self.switch_spiderman.pack(padx=10, pady=5, anchor="w")

        # System Monitor Section
        self.monitor_group = ctk.CTkFrame(self.control_frame)
        self.monitor_group.pack(padx=15, pady=15, fill="x")

        self.lbl_monitor = ctk.CTkLabel(
            self.monitor_group,
            text="📊 System Status",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_monitor.pack(padx=10, pady=5, anchor="w")

        self.fps_label = ctk.CTkLabel(self.monitor_group, text="FPS: --", font=ctk.CTkFont(size=12))
        self.fps_label.pack(padx=10, pady=2, anchor="w")

        self.status_label = ctk.CTkLabel(self.monitor_group, text="Status: Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(padx=10, pady=2, anchor="w")

    def update_feed(self):
        ret, frame = self.cap.read()
        if not ret:
            self.after(10, self.update_feed)
            return

        # Calculate FPS
        curr_time = time.time()
        fps = int(1 / (curr_time - self.prev_time + 1e-5))
        self.prev_time = curr_time
        self.fps_label.configure(text=f"FPS: {fps}")

        frame = cv2.flip(frame, 1)

        # 1. PLAYBACK VIDEO MEME (Jika Aktif)
        if self.active_video and self.active_video.is_playing:
            video_frame = self.active_video.get_frame()
            if video_frame is not None:
                display_frame = cv2.resize(video_frame, (frame.shape[1], frame.shape[0]))
                self.status_label.configure(text="Status: Playing Video Meme!")
                self._render_to_label(display_frame)
                self.after(10, self.update_feed)
                return
            else:
                self.active_video.close()
                self.active_video = None

        # 2. DETEKSI POSE NORMAL
        landmarks = self.engine.process_frame(frame)
        self.status_label.configure(text="Status: Detecting Pose...")

        # 3. TRIGGER CHECKING
        if self.switch_jokowi.get() and self.engine.check_jokowi_pose(landmarks):
            self.status_label.configure(text="Trigger: Jokowi Pose!")
            self.active_video = MemeVideoPlayer(MEME_REGISTRY["jokowi_berjuang"]["path"])

        elif self.switch_spiderman.get() and self.engine.check_spiderman_pose(landmarks):
            self.status_label.configure(text="Trigger: Spiderman Pose!")
            if self.spiderman_img is not None:
                frame = overlay_transparent(frame, self.spiderman_img, x=30, y=30, size=(180, 180))

        self._render_to_label(frame)
        self.after(10, self.update_feed)

    def _render_to_label(self, frame):
        """Konversi Frame BGR OpenCV ke Image Format CustomTkinter"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)
        ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(720, 540))
        self.video_label.configure(image=ctk_image)

    def on_closing(self):
        if self.active_video:
            self.active_video.close()
        self.cap.release()
        self.destroy()