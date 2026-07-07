import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List

mp_hands = mp.solutions.hands

class HandTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.results = None
        self.landmarks = None
        self.frame_count = 0
        self.gesture_count = 0
    
    def process(self, frame: np.ndarray) -> Dict:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb)
        self.frame_count += 1
        
        features = {}
        
        if not self.results or not self.results.multi_hand_landmarks:
            return self._default_features()
        
        self.landmarks = self.results.multi_hand_landmarks[0]
        self.gesture_count += 1
        
        features['gesture_frequency'] = min(100, self.gesture_count / 10)
        features['gesture_speed'] = 50.0
        features['gesture_amplitude'] = self._calc_gesture_amplitude()
        features['gesture_symmetry'] = 50.0
        features['gesture_speech_sync'] = 50.0
        features['adapter_gestures'] = 10.0
        features['emblem_gestures'] = 10.0
        features['pointing'] = self._calc_pointing()
        features['open_palm'] = self._calc_open_palm()
        features['finger_tapping'] = 10.0
        features['hand_clasping'] = 10.0
        features['hand_wringing'] = 10.0
        
        return features
    
    def _default_features(self) -> Dict:
        return {
            'gesture_frequency': 30.0,
            'gesture_speed': 40.0,
            'gesture_amplitude': 40.0,
            'gesture_symmetry': 50.0,
            'gesture_speech_sync': 50.0,
            'adapter_gestures': 10.0,
            'emblem_gestures': 10.0,
            'pointing': 5.0,
            'open_palm': 50.0,
            'finger_tapping': 10.0,
            'hand_clasping': 10.0,
            'hand_wringing': 10.0
        }
    
    def _get_point(self, idx: int):
        return self.landmarks.landmark[idx]
    
    def _distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    def _calc_gesture_amplitude(self) -> float:
        thumb = self._get_point(4)
        pinky = self._get_point(20)
        spread = self._distance(thumb, pinky)
        score = spread * 100
        return max(0, min(100, score))
    
    def _calc_pointing(self) -> float:
        index_tip = self._get_point(8)
        index_mcp = self._get_point(5)
        extended = self._distance(index_tip, index_mcp) > 0.1
        return 70.0 if extended else 10.0
    
    def _calc_open_palm(self) -> float:
        tips = [4, 8, 12, 16, 20]
        mcp = [2, 5, 9, 13, 17]
        
        extended = 0
        for tip, base in zip(tips, mcp):
            if self._distance(self._get_point(tip), self._get_point(base)) > 0.05:
                extended += 1
        
        score = (extended / 5) * 100
        return max(0, min(100, score))