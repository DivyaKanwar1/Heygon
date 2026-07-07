from typing import Dict
from logger import logger
from aggregator import FeatureAggregator
from scorer import ExecutiveScorer

def process_video_background(video_path: str) -> Dict:
    logger.info(f"Background processing started: {video_path}")
    
    try:
        aggregator = FeatureAggregator()
        features = aggregator.extract_all(video_path)
        
        scorer = ExecutiveScorer()
        scores = scorer.calculate(features)
        
        logger.info(f"Background processing complete: {scores.get('overall', 0)}")
        
        return {
            'success': True,
            'features': features,
            'scores': scores
        }
        
    except Exception as e:
        logger.error(f"Background processing failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }