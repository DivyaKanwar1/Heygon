from typing import Dict, List
import numpy as np

class TemporalTracker:
    def __init__(self):
        self.feature_history = []
        self.total_frames = 0
    
    def add_frame(self, features: Dict):
        self.feature_history.append(features)
        self.total_frames += 1
    
    def calculate(self) -> Dict:
        features = {}
        
        if len(self.feature_history) < 10:
            return self._default_features()
        
        features['trend_over_time'] = self._calc_trend()
        features['stress_recovery'] = 60.0
        features['question_response'] = 70.0
        features['first_vs_last'] = self._calc_first_last()
        features['pattern_consistency'] = self._calc_consistency()
        
        return features
    
    def _default_features(self) -> Dict:
        return {
            'trend_over_time': 50.0,
            'stress_recovery': 60.0,
            'question_response': 70.0,
            'first_vs_last': 50.0,
            'pattern_consistency': 70.0
        }
    
    def _calc_trend(self) -> float:
        eye_contact_values = [
            f.get('eye_contact', 50) 
            for f in self.feature_history 
            if 'eye_contact' in f
        ]
        
        if len(eye_contact_values) < 2:
            return 50.0
        
        first_half = np.mean(eye_contact_values[:len(eye_contact_values)//2])
        second_half = np.mean(eye_contact_values[len(eye_contact_values)//2:])
        
        if second_half > first_half:
            return 60.0 + (second_half - first_half) * 0.2
        else:
            return 60.0 - (first_half - second_half) * 0.2
    
    def _calc_first_last(self) -> float:
        if len(self.feature_history) < 10:
            return 50.0
        
        first_third = self.feature_history[:len(self.feature_history)//3]
        last_third = self.feature_history[len(self.feature_history)//3*2:]
        
        first_scores = [f.get('eye_contact', 50) for f in first_third if 'eye_contact' in f]
        last_scores = [f.get('eye_contact', 50) for f in last_third if 'eye_contact' in f]
        
        if first_scores and last_scores:
            diff = np.mean(last_scores) - np.mean(first_scores)
            return 50 + diff * 0.5
        
        return 50.0
    
    def _calc_consistency(self) -> float:
        eye_contact_values = [
            f.get('eye_contact', 50) 
            for f in self.feature_history 
            if 'eye_contact' in f
        ]
        
        if len(eye_contact_values) < 2:
            return 70.0
        
        variance = np.var(eye_contact_values)
        score = 100 - (variance * 0.5)
        return max(0, min(100, score))