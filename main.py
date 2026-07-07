from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json
import tempfile
import time
import asyncio
import cv2
import numpy as np
from typing import Dict, List, Optional, Set
import base64
import shutil

from config import settings
from logger import logger
from helpers import validate_video, get_video_duration, cleanup_temp, safe_get, format_duration, Timer
from face_tracker import FaceTracker
from pose_tracker import PoseTracker
from hand_tracker import HandTracker
from audio_tracker import AudioTracker
from environment_tracker import EnvironmentTracker
from temporal_tracker import TemporalTracker
from aggregator import FeatureAggregator
from scorer import ExecutiveScorer
from video_processor import process_video_background
from report_generator import generate_report
from storage import save_report, get_report, delete_report, report_exists

# Create FastAPI app
app = FastAPI(
    title="Paragon IRIS",
    description="Executive Interview Intelligence - 77 Features",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files from current directory (flat structure)
app.mount("/static", StaticFiles(directory="."), name="static")

# WebSocket connections
active_connections: Set[WebSocket] = set()

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/favicon.ico")
async def favicon():
    return FileResponse("favicon.ico")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Paragon IRIS",
        "version": "1.0.0",
        "features": 77,
        "timestamp": time.time()
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong'})
                elif msg.get('type') == 'frame':
                    img_data = base64.b64decode(msg['image'])
                    np_arr = np.frombuffer(img_data, np.uint8)
                    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    
                    h, w = frame.shape[:2]
                    await websocket.send_json({
                        'type': 'scores',
                        'eye_contact': 85.0,
                        'posture': 78.0,
                        'gestures': 72.0,
                        'overall': 80.0,
                        'timestamp': time.time()
                    })
            except Exception as e:
                logger.error(f"WebSocket message error: {e}")
                await websocket.send_json({'type': 'error', 'message': str(e)})
                
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info("WebSocket disconnected")

@app.post("/api/analyze")
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    candidate_name: str = "Unknown",
    role: str = "Executive"
):
    if not file.filename:
        raise HTTPException(400, "No file provided")
    
    if not validate_video(file.filename):
        raise HTTPException(400, "Only video files supported")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        duration = get_video_duration(tmp_path)
        logger.info(f"Processing: {file.filename}, duration: {duration}s")
        
        aggregator = FeatureAggregator()
        features = aggregator.extract_all(tmp_path)
        
        scorer = ExecutiveScorer()
        scores = scorer.calculate(features)
        overall = scores.get('overall', 0)
        
        report_id = f"report_{int(time.time())}_{candidate_name.replace(' ', '_')}"
        
        background_tasks.add_task(
            generate_report,
            tmp_path,
            candidate_name,
            role,
            features,
            scores,
            report_id
        )
        
        return JSONResponse({
            "success": True,
            "candidate": candidate_name,
            "role": role,
            "duration": duration,
            "overall_score": overall,
            "scores": scores,
            "features": features,
            "report_id": report_id
        })
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        cleanup_temp(tmp_path)
        raise HTTPException(500, f"Analysis failed: {str(e)}")
    finally:
        background_tasks.add_task(cleanup_temp, tmp_path)

@app.get("/api/report/{report_id}")
async def download_report(report_id: str):
    if not report_exists(report_id):
        raise HTTPException(404, "Report not found or expired")
    return FileResponse(
        get_report(report_id),
        filename=f"paragon_iris_{report_id}.pdf"
    )

@app.delete("/api/report/{report_id}")
async def delete_report_endpoint(report_id: str):
    if delete_report(report_id):
        return {"success": True, "message": "Report deleted"}
    raise HTTPException(404, "Report not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10000,
        reload=settings.ENV == "development"
    )