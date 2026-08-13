# main.py
"""
Main Entry Point untuk menjalankan Aplikasi GUI Meme-ify Me.
"""
from gui_app import MemeifyApp


def main():
    app = MemeifyApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()