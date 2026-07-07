import os
from typing import List

class Settings:
    ENV = os.getenv("ENV", "production")
    PORT = int(os.getenv("PORT", 10000))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    CORS_ORIGINS = [
        "*",
        "chrome-extension://*",
        "https://*.onrender.com",
        "http://localhost:*"
    ]
    
    MAX_VIDEO_SIZE = 500 * 1024 * 1024
    MAX_VIDEO_DURATION = 7200
    REPORT_RETENTION_DAYS = 7
    
    TARGET_FPS = 5
    FRAME_SKIP = 6
    
    REPORT_DIR = "/tmp/reports"
    TEMP_DIR = "/tmp"
    
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        os.makedirs(self.REPORT_DIR, exist_ok=True)

settings = Settings()