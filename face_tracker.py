import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Optional

mp_face = mp.solutions.face_mesh

class FaceTracker:
    def __init__(self):
        self.face_mesh = mp_face.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.LEFT_IRIS = 468
        self.RIGHT_IRIS = 473
        self.NOSE_TIP = 1
        self.NOSE_BRIDGE = 4
        self.MOUTH_LEFT = 61
        self.MOUTH_RIGHT = 291
        self.MOUTH_TOP = 13
        self.MOUTH_BOTTOM = 14
        self.EYEBROW_LEFT = [46, 53, 65]
        self.EYEBROW_RIGHT = [276, 283, 295]
        self.EYE_LEFT = [33, 133, 157, 158, 159, 160, 161, 173]
        self.EYE_RIGHT = [362, 263, 387, 386, 385, 384, 398, 466]
        
        self.results = None
        self.landmarks = None
    
    def process(self, frame: np.ndarray) -> Dict:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(rgb)
        
        features = {}
        
        if not self.results or not self.results.multi_face_landmarks:
            return self._default_features()
        
        self.landmarks = self.results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        features['eye_contact'] = self._calc_eye_contact()
        features['blink_rate'] = self._calc_blink_rate()
        features['smile_intensity'] = self._calc_smile()
        features['eyebrow_height'] = self._calc_eyebrow_height()
        features['jaw_tension'] = self._calc_jaw_tension()
        features['mouth_asymmetry'] = self._calc_mouth_asymmetry()
        features['head_pitch'] = self._calc_head_pose()[0]
        features['head_yaw'] = self._calc_head_pose()[1]
        features['head_roll'] = self._calc_head_pose()[2]
        features['gaze_aversion'] = self._calc_gaze_aversion()
        features['facial_symmetry'] = self._calc_facial_symmetry()
        features['eyebrow_furrow'] = self._calc_eyebrow_furrow()
        features['lip_compression'] = self._calc_lip_compression()
        features['cheek_raise'] = self._calc_cheek_raise()
        features['nose_wrinkle'] = 10.0
        features['emotional_valence'] = self._calc_emotional_valence()
        features['emotional_arousal'] = self._calc_emotional_arousal()
        features['facial_flush'] = 50.0
        
        return features
    
    def _default_features(self) -> Dict:
        return {
            'eye_contact': 50.0,
            'blink_rate': 12.0,
            'smile_intensity': 30.0,
            'eyebrow_height': 50.0,
            'jaw_tension': 30.0,
            'mouth_asymmetry': 20.0,
            'head_pitch': 0.0,
            'head_yaw': 0.0,
            'head_roll': 0.0,
            'gaze_aversion': 0.0,
            'facial_symmetry': 80.0,
            'eyebrow_furrow': 20.0,
            'lip_compression': 20.0,
            'cheek_raise': 30.0,
            'nose_wrinkle': 10.0,
            'emotional_valence': 60.0,
            'emotional_arousal': 50.0,
            'facial_flush': 50.0
        }
    
    def _get_point(self, idx: int):
        return self.landmarks.landmark[idx]
    
    def _distance(self, p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
    
    def _calc_eye_contact(self) -> float:
        left_iris = self._get_point(self.LEFT_IRIS)
        right_iris = self._get_point(self.RIGHT_IRIS)
        nose = self._get_point(self.NOSE_TIP)
        
        left_dist = self._distance(left_iris, nose)
        right_dist = self._distance(right_iris, nose)
        avg_dist = (left_dist + right_dist) / 2
        
        score = 100 - (avg_dist * 400)
        return max(0, min(100, score))
    
    def _calc_blink_rate(self) -> float:
        left_eye = [self._get_point(i) for i in self.EYE_LEFT]
        right_eye = [self._get_point(i) for i in self.EYE_RIGHT]
        
        def ear(pts):
            p1, p2, p3, p4, p5, p6 = pts[0], pts[1], pts[2], pts[3], pts[4], pts[5]
            v1 = self._distance(p2, p6)
            v2 = self._distance(p3, p5)
            h = self._distance(p1, p4)
            return (v1 + v2) / (2 * h + 1e-6)
        
        left_ear = ear(left_eye)
        right_ear = ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2
        
        return max(0, min(100, avg_ear * 300))
    
    def _calc_smile(self) -> float:
        left = self._get_point(self.MOUTH_LEFT)
        right = self._get_point(self.MOUTH_RIGHT)
        top = self._get_point(self.MOUTH_TOP)
        bottom = self._get_point(self.MOUTH_BOTTOM)
        
        width = self._distance(left, right)
        height = self._distance(top, bottom)
        
        ratio = width / (height + 1e-6)
        score = (ratio - 0.8) * 100
        return max(0, min(100, score))
    
    def _calc_eyebrow_height(self) -> float:
        left_brow = self._get_point(self.EYEBROW_LEFT[1])
        left_eye = self._get_point(self.EYE_LEFT[0])
        diff = left_brow.y - left_eye.y
        return max(0, min(100, 100 - (diff * 200)))
    
    def _calc_jaw_tension(self) -> float:
        left = self._get_point(self.MOUTH_LEFT)
        right = self._get_point(self.MOUTH_RIGHT)
        width = self._distance(left, right)
        score = 100 - (width * 300)
        return max(0, min(100, score))
    
    def _calc_mouth_asymmetry(self) -> float:
        left = self._get_point(self.MOUTH_LEFT)
        right = self._get_point(self.MOUTH_RIGHT)
        asymmetry = abs(left.y - right.y) * 200
        return max(0, min(100, asymmetry))
    
    def _calc_head_pose(self) -> tuple:
        nose = self._get_point(self.NOSE_TIP)
        nose_bridge = self._get_point(self.NOSE_BRIDGE)
        
        pitch = (nose.y - nose_bridge.y) * 200
        yaw = (nose.x - 0.5) * 200
        roll = 0.0
        
        return (max(-100, min(100, pitch)), max(-100, min(100, yaw)), max(-100, min(100, roll)))
    
    def _calc_gaze_aversion(self) -> float:
        left_iris = self._get_point(self.LEFT_IRIS)
        right_iris = self._get_point(self.RIGHT_IRIS)
        
        left_aversion = abs(left_iris.x - 0.5) * 200
        right_aversion = abs(right_iris.x - 0.5) * 200
        avg = (left_aversion + right_aversion) / 2
        return max(0, min(100, avg))
    
    def _calc_facial_symmetry(self) -> float:
        left_eye = self._get_point(self.EYE_LEFT[0])
        right_eye = self._get_point(self.EYE_RIGHT[0])
        
        diff_x = abs(left_eye.x - (1 - right_eye.x))
        diff_y = abs(left_eye.y - right_eye.y)
        score = 100 - ((diff_x + diff_y) * 150)
        return max(0, min(100, score))
    
    def _calc_eyebrow_furrow(self) -> float:
        left = self._get_point(self.EYEBROW_LEFT[1])
        right = self._get_point(self.EYEBROW_RIGHT[1])
        avg_y = (left.y + right.y) / 2
        score = (0.5 - avg_y) * 200
        return max(0, min(100, score))
    
    def _calc_lip_compression(self) -> float:
        top = self._get_point(self.MOUTH_TOP)
        bottom = self._get_point(self.MOUTH_BOTTOM)
        height = self._distance(top, bottom)
        score = 100 - (height * 300)
        return max(0, min(100, score))
    
    def _calc_cheek_raise(self) -> float:
        return self._calc_smile() * 0.8
    
    def _calc_emotional_valence(self) -> float:
        smile = self._calc_smile()
        brow = self._calc_eyebrow_furrow()
        valence = (smile * 0.7) + ((100 - brow) * 0.3)
        return max(0, min(100, valence))
    
    def _calc_emotional_arousal(self) -> float:
        eye_contact = self._calc_eye_contact()
        blink = self._calc_blink_rate()
        arousal = (eye_contact * 0.5) + ((100 - blink) * 0.5)
        return max(0, min(100, arousal))