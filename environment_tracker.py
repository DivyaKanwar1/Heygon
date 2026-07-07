import cv2
import numpy as np
from typing import Dict

class EnvironmentTracker:
    def __init__(self):
        self.prev_frame = None
    
    def process(self, frame: np.ndarray) -> Dict:
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        features = {}
        
        features['background_clutter'] = self._calc_clutter(frame)
        features['lighting_quality'] = self._calc_lighting(gray)
        features['camera_angle'] = 70.0
        features['background_noise'] = 20.0
        features['background_motion'] = self._calc_background_motion(frame)
        features['framing_quality'] = 75.0
        features['virtual_background'] = 30.0
        features['background_consistency'] = self._calc_consistency(frame)
        features['environment_change'] = 10.0
        features['echo_reverb'] = 20.0
        
        self.prev_frame = gray.copy()
        
        return features
    
    def _default_features(self) -> Dict:
        return {
            'background_clutter': 20.0,
            'lighting_quality': 70.0,
            'camera_angle': 50.0,
            'background_noise': 20.0,
            'background_motion': 10.0,
            'framing_quality': 70.0,
            'virtual_background': 30.0,
            'background_consistency': 80.0,
            'environment_change': 10.0,
            'echo_reverb': 20.0
        }
    
    def _calc_clutter(self, frame: np.ndarray) -> float:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        score = edge_density * 200
        return max(0, min(100, score))
    
    def _calc_lighting(self, gray: np.ndarray) -> float:
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        mean_score = 100 - abs(mean_brightness - 128) * 0.5
        std_score = 100 - std_brightness * 0.5
        
        score = (mean_score * 0.6 + std_score * 0.4)
        return max(0, min(100, score))
    
    def _calc_background_motion(self, frame: np.ndarray) -> float:
        if self.prev_frame is None:
            return 10.0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, self.prev_frame)
        motion = np.sum(diff > 30) / diff.size
        score = motion * 200
        return max(0, min(100, score))
    
    def _calc_consistency(self, frame: np.ndarray) -> float:
        if self.prev_frame is None:
            return 80.0
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, self.prev_frame)
        change = np.mean(diff) / 255
        score = 100 - (change * 100)
        return max(0, min(100, score))