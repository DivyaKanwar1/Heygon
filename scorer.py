from typing import Dict

class ExecutiveScorer:
    def __init__(self):
        self.weights = {
            'composure': 0.30,
            'communication': 0.25,
            'presence': 0.25,
            'professionalism': 0.20
        }
    
    def calculate(self, features: Dict) -> Dict:
        face = features.get('face', {})
        pose = features.get('pose', {})
        hands = features.get('hands', {})
        audio = features.get('audio', {})
        env = features.get('environment', {})
        temporal = features.get('temporal', {})
        
        composure = (
            face.get('eye_contact', 50) * 0.20 +
            face.get('jaw_tension', 50) * 0.10 +
            face.get('head_pitch', 50) * 0.10 +
            face.get('gaze_aversion', 50) * 0.15 +
            pose.get('fidget_intensity', 50) * 0.15 +
            pose.get('shoulder_squareness', 50) * 0.10 +
            temporal.get('stress_recovery', 50) * 0.20
        )
        
        communication = (
            audio.get('speaking_pace', 50) * 0.15 +
            audio.get('pitch_variability', 50) * 0.10 +
            audio.get('volume_variability', 50) * 0.10 +
            audio.get('filler_rate', 50) * 0.15 +
            audio.get('pause_duration', 50) * 0.10 +
            audio.get('sentence_completion', 50) * 0.15 +
            face.get('smile_intensity', 50) * 0.10 +
            temporal.get('question_response', 50) * 0.15
        )
        
        presence = (
            pose.get('posture_consistency', 50) * 0.20 +
            face.get('eye_contact', 50) * 0.20 +
            face.get('facial_symmetry', 50) * 0.10 +
            hands.get('gesture_frequency', 50) * 0.10 +
            hands.get('open_palm', 50) * 0.10 +
            pose.get('sitting_depth', 50) * 0.10 +
            temporal.get('trend_over_time', 50) * 0.20
        )
        
        professionalism = (
            env.get('background_clutter', 50) * 0.20 +
            env.get('lighting_quality', 50) * 0.20 +
            env.get('framing_quality', 50) * 0.20 +
            env.get('virtual_background', 50) * 0.15 +
            env.get('background_consistency', 50) * 0.15 +
            audio.get('background_noise', 50) * 0.10
        )
        
        overall = (
            composure * self.weights['composure'] +
            communication * self.weights['communication'] +
            presence * self.weights['presence'] +
            professionalism * self.weights['professionalism']
        )
        
        return {
            'overall': round(overall, 1),
            'composure': round(composure, 1),
            'communication': round(communication, 1),
            'presence': round(presence, 1),
            'professionalism': round(professionalism, 1),
            'feature_count': 77
        }