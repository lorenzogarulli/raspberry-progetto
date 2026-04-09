import subprocess
import os
import signal

# Percorsi dei video (mettili nella cartella "video" accanto a questo file)
VIDEO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video")
VIDEO_LOOP = os.path.join(VIDEO_DIR, "loop.mp4")
VIDEO_EVENTO = os.path.join(VIDEO_DIR, "evento.mp4")

_processo_video = None


def _kill_video():
    """Ferma il video attualmente in riproduzione."""
    global _processo_video
    if _processo_video and _processo_video.poll() is None:
        _processo_video.terminate()
        try:
            _processo_video.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _processo_video.kill()
    _processo_video = None


def avvia_loop():
    """Avvia il video in loop (gira all'infinito su HDMI)."""
    global _processo_video
    _kill_video()
    if not os.path.exists(VIDEO_LOOP):
        print(f"Video loop non trovato: {VIDEO_LOOP}")
        return
    _processo_video = subprocess.Popen(
        ["mpv", "--fs", "--loop=inf", "--no-terminal", "--no-osc", VIDEO_LOOP],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Video loop avviato: {VIDEO_LOOP}")


def avvia_evento():
    """Avvia il video evento (1 minuto, poi torna al loop)."""
    global _processo_video
    _kill_video()
    if not os.path.exists(VIDEO_EVENTO):
        print(f"Video evento non trovato: {VIDEO_EVENTO}")
        return
    _processo_video = subprocess.Popen(
        ["mpv", "--fs", "--no-terminal", "--no-osc", VIDEO_EVENTO],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print(f"Video evento avviato: {VIDEO_EVENTO}")


def ferma():
    """Ferma qualsiasi video in riproduzione."""
    _kill_video()
    print("Video fermato")
