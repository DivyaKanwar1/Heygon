import cv2
import mediapipe as mp
import numpy as np
from typing import Dict

mp_pose = mp.solutions.pose

class PoseTracker:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.results = None
        self.landmarks = None
    
    def process(self, frame: np.ndarray) -> Dict:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(rgb)
        
        features = {}
        
        if not self.results or not self.results.pose_landmarks:
            return self._default_features()
        
        self.landmarks = self.results.pose_landmarks.landmark
        h, w = frame.shape[:2]
        
        features['lean_angle'] = self._calc_lean()
        features['shoulder_squareness'] = self._calc_shoulders()
        features['chin_height'] = self._calc_chin()
        features['arm_crossed'] = self._calc_arm_cross()
        features['hand_visibility'] = self._calc_hand_visibility()
        features['fidget_intensity'] = 20.0
        features['posture_consistency'] = 70.0
        features['mirroring'] = 50.0
        features['sitting_depth'] = self._calc_sitting_depth()
        features['body_orientation'] = self._calc_orientation()
        features['trunk_rotation'] = 0.0
        features['head_tilt'] = self._calc_head_tilt()
        features['shoulder_asymmetry'] = self._calc_shoulder_asymmetry()
        features['leg_bounce'] = 20.0
        
        return features
    
    def _default_features(self) -> Dict:
        return {
            'lean_angle': 50.0,
            'shoulder_squareness': 70.0,
            'chin_height': 50.0,
            'arm_crossed': 10.0,
            'hand_visibility': 50.0,
            'fidget_intensity': 20.0,
            'posture_consistency': 70.0,
            'mirroring': 50.0,
            'sitting_depth': 50.0,
            'body_orientation': 50.0,
            'trunk_rotation': 0.0,
            'head_tilt': 50.0,
            'shoulder_asymmetry': 20.0,
            'leg_bounce': 20.0
        }
    
    def _get_point(self, idx: int):
        return self.landmarks[idx]
    
    def _distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    def _calc_lean(self) -> float:
        left_shoulder = self._get_point(11)
        right_shoulder = self._get_point(12)
        left_hip = self._get_point(23)
        right_hip = self._get_point(24)
        
        shoulder_center = (
            (left_shoulder.x + right_shoulder.x) / 2,
            (left_shoulder.y + right_shoulder.y) / 2
        )
        hip_center = (
            (left_hip.x + right_hip.x) / 2,
            (left_hip.y + right_hip.y) / 2
        )
        
        angle = np.arctan2(
            shoulder_center[1] - hip_center[1],
            shoulder_center[0] - hip_center[0]
        )
        
        score = 50 - (angle * 100)
        return max(0, min(100, score))
    
    def _calc_shoulders(self) -> float:
        left = self._get_point(11)
        right = self._get_point(12)
        diff = abs(left.z - right.z)
        score = 100 - (diff * 200)
        return max(0, min(100, score))
    
    def _calc_chin(self) -> float:
        chin = self._get_point(152)
        score = (1 - chin.y) * 100
        return max(0, min(100, score))
    
    def _calc_arm_cross(self) -> float:
        left_wrist = self._get_point(15)
        right_wrist = self._get_point(16)
        left_shoulder = self._get_point(11)
        right_shoulder = self._get_point(12)
        
        left_cross = self._distance(left_wrist, right_shoulder)
        right_cross = self._distance(right_wrist, left_shoulder)
        
        if left_cross < 0.2 and right_cross < 0.2:
            return 80.0
        return 10.0
    
    def _calc_hand_visibility(self) -> float:
        left_wrist = self._get_point(15)
        right_wrist = self._get_point(16)
        
        visible = 0
        if 0 < left_wrist.x < 1 and 0 < left_wrist.y < 1:
            visible += 1
        if 0 < right_wrist.x < 1 and 0 < right_wrist.y < 1:
            visible += 1
        
        return (visible / 2) * 100
    
    def _calc_sitting_depth(self) -> float:
        left_shoulder = self._get_point(11)
        left_hip = self._get_point(23)
        dist = self._distance(left_shoulder, left_hip)
        score = 100 - (dist * 300)
        return max(0, min(100, score))
    
    def _calc_orientation(self) -> float:
        left = self._get_point(11)
        right = self._get_point(12)
        diff = abs(left.x - right.x)
        score = 100 - (diff * 200)
        return max(0, min(100, score))
    
    def _calc_head_tilt(self) -> float:
        ear_left = self._get_point(7)
        ear_right = self._get_point(8)
        ear_diff = abs(ear_left.y - ear_right.y)
        score = ear_diff * 200
        return max(0, min(100, score))
    
    def _calc_shoulder_asymmetry(self) -> float:
        left = self._get_point(11)
        right = self._get_point(12)
        diff = abs(left.y - right.y)
        score = diff * 200
        return max(0, min(100, score))