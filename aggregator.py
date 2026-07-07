import cv2
import numpy as np
from typing import Dict, List
from face_tracker import FaceTracker
from pose_tracker import PoseTracker
from hand_tracker import HandTracker
from audio_tracker import AudioTracker
from environment_tracker import EnvironmentTracker
from temporal_tracker import TemporalTracker
from logger import logger

class FeatureAggregator:
    def __init__(self):
        self.face_tracker = FaceTracker()
        self.pose_tracker = PoseTracker()
        self.hand_tracker = HandTracker()
        self.audio_tracker = AudioTracker()
        self.environment_tracker = EnvironmentTracker()
        self.temporal_tracker = TemporalTracker()
    
    def extract_all(self, video_path: str) -> Dict:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Cannot open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0
        
        logger.info(f"Processing video: {duration:.1f}s, {total_frames} frames")
        
        aggregated = {
            'face': {},
            'pose': {},
            'hands': {},
            'environment': {},
            'temporal': {}
        }
        
        face_history = []
        pose_history = []
        hand_history = []
        env_history = []
        
        frame_count = 0
        processed = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            if frame_count % 6 != 0:
                continue
            
            processed += 1
            
            face_features = self.face_tracker.process(frame)
            face_history.append(face_features)
            
            pose_features = self.pose_tracker.process(frame)
            pose_history.append(pose_features)
            
            hand_features = self.hand_tracker.process(frame)
            hand_history.append(hand_features)
            
            env_features = self.environment_tracker.process(frame)
            env_history.append(env_features)
            
            all_features = {**face_features, **pose_features, **hand_features, **env_features}
            self.temporal_tracker.add_frame(all_features)
            
            if processed % 100 == 0:
                logger.info(f"Processed {processed} frames")
        
        cap.release()
        
        face_avg = self._average_dicts(face_history)
        for key, value in face_avg.items():
            aggregated['face'][key] = value
        
        pose_avg = self._average_dicts(pose_history)
        for key, value in pose_avg.items():
            aggregated['pose'][key] = value
        
        hand_avg = self._average_dicts(hand_history)
        for key, value in hand_avg.items():
            aggregated['hands'][key] = value
        
        env_avg = self._average_dicts(env_history)
        for key, value in env_avg.items():
            aggregated['environment'][key] = value
        
        audio_features = self.audio_tracker.extract_from_video(video_path)
        aggregated['audio'] = audio_features
        
        temporal_features = self.temporal_tracker.calculate()
        aggregated['temporal'] = temporal_features
        
        aggregated['_meta'] = {
            'duration': duration,
            'fps': fps,
            'frames_processed': processed,
            'total_frames': total_frames
        }
        
        logger.info(f"Extraction complete: {processed} frames processed")
        
        return aggregated
    
    def _average_dicts(self, dicts: List[Dict]) -> Dict:
        if not dicts:
            return {}
        
        keys = dicts[0].keys()
        averaged = {}
        
        for key in keys:
            values = [d.get(key, 0) for d in dicts if key in d]
            if values:
                averaged[key] = round(np.mean(values), 2)
            else:
                averaged[key] = 50.0
        
        return averaged