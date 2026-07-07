import os
import shutil
from config import settings
from logger import logger

def save_report(report_id: str, file_path: str) -> str:
    os.makedirs(settings.REPORT_DIR, exist_ok=True)
    dest_path = os.path.join(settings.REPORT_DIR, f"{report_id}.pdf")
    shutil.copy(file_path, dest_path)
    logger.info(f"Report saved: {dest_path}")
    return dest_path

def get_report(report_id: str) -> str:
    return os.path.join(settings.REPORT_DIR, f"{report_id}.pdf")

def report_exists(report_id: str) -> bool:
    return os.path.exists(get_report(report_id))

def delete_report(report_id: str) -> bool:
    path = get_report(report_id)
    if os.path.exists(path):
        os.unlink(path)
        logger.info(f"Report deleted: {path}")
        return True
    return False

def cleanup_old_reports(days: int = 7):
    import time
    now = time.time()
    cutoff = now - (days * 86400)
    
    for filename in os.listdir(settings.REPORT_DIR):
        if filename.endswith('.pdf'):
            path = os.path.join(settings.REPORT_DIR, filename)
            if os.path.getmtime(path) < cutoff:
                os.unlink(path)
                logger.info(f"Cleaned old report: {path}")