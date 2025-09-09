"""
Confidence Calibrator Module
Calibrates confidence scores based on historical performance
"""
from typing import Dict, Optional


class ConfidenceCalibrator:
    """Calibrates confidence scores"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.calibration_factors = {
            'PLATINUM': 0.95,
            'GOLD': 0.85,
            'SILVER': 0.75,
            'BRONZE': 0.65
        }
        
    def calibrate(self, confidence: float, tier: str) -> float:
        """
        Calibrate confidence score based on tier
        
        Args:
            confidence: Raw confidence score
            tier: Signal tier
            
        Returns:
            Calibrated confidence score
        """
        factor = self.calibration_factors.get(tier, 0.7)
        calibrated = confidence * factor
        
        # Ensure within bounds
        return max(0, min(100, calibrated))