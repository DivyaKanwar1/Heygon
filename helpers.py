import os
import cv2
import time
import tempfile
from typing import Dict, Any, Optional
from logger import logger

def validate_video(filename: str) -> bool:
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    return filename.lower().endswith(video_extensions)

def get_video_duration(file_path: str) -> float:
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return 0.0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    if fps == 0:
        return 0.0
    return frame_count / fps

def cleanup_temp(file_path: str):
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        logger.warning(f"Failed to delete {file_path}: {e}")

def format_duration(seconds: int) -> str:
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"

def safe_get(obj: Dict, keys: list, default=None):
    for key in keys:
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return default
    return obj if obj is not None else default

class Timer:
    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start = None
    
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start
        logger.info(f"{self.name} took {elapsed:.2f}s")