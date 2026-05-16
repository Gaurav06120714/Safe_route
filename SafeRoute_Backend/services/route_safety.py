import logging
from datetime import datetime
from typing import Optional, Tuple, Dict, List
from core.safety_config import WEIGHTS, MAX_VALUES, get_time_multiplier
from services.familiarity_module import FamiliarityScoreCalculator

logger = logging.getLogger(__name__)

class DataNormalizationLayer:
    """Standardizes raw inputs into normalized 0-1 metrics."""
    
    @staticmethod
    def normalize_crime(density: float) -> float:
        return min(density / MAX_VALUES["crime"], 1.0)
    
    @staticmethod
    def normalize_cctv(count: int) -> float:
        return min(count / MAX_VALUES["cctv"], 1.0)
    
    @staticmethod
    def normalize_crowd(density: float) -> float:
        return min(density / MAX_VALUES["crowd"], 1.0)
    
    @staticmethod
    def normalize_vibrancy(safe_points: int) -> float:
        return min(safe_points / MAX_VALUES["vibrancy"], 1.0)

def calculate_safety_score(segment: dict, hour: int, familiarity_score: float = FamiliarityScoreCalculator.BASE_SCORE) -> tuple[float, dict[str, float]]:
    """
    Calculates final segment safety score and provides a breakdown of component impacts.
    Hierarchy: Crime(0.4) > CCTV/Light(0.2 ea) > Fam/RoadType(0.1 ea).
    """
    
    # 1. Component Normalization & Temporal Scaling
    time_mult = get_time_multiplier(hour)
    
    # CRIME Factor (Highest Priority: 40%)
    base_density = segment.get("crime_density", 0.0)
    report_count = segment.get("incident_report_count", 0)
    sev_avg      = segment.get("incident_severity_avg", 0.0)
    incident_boost = (sev_avg / 10.0) * min(report_count * 0.2, 1.0)
    
    raw_crime_risk = base_density + incident_boost
    effective_crime_risk = min(raw_crime_risk * time_mult, 2.0)
    crime_safety_norm = 1.0 - min(effective_crime_risk / 2.0, 1.0)
    
    # CCTV & LIGHTING Factors (Moderate Priority: 20% each)
    cctv_norm     = DataNormalizationLayer.normalize_cctv(segment.get("cctv_count", 0))
    lighting_norm = DataNormalizationLayer.normalize_vibrancy(
        5 if segment.get("safe_zone_flag", False) else 0 
    )
    
    # FAMILIARITY & ROAD TYPE Factors (Lower Priority: 10% each)
    fam_norm = 1.0 if familiarity_score > FamiliarityScoreCalculator.BASE_SCORE else 0.5
    
    raw_crowd_norm = DataNormalizationLayer.normalize_crowd(segment.get("crowd_density", 0))
    road_risk = 1.0 - raw_crowd_norm
    effective_road_risk = min(road_risk * time_mult, 1.0)
    road_type_norm = 1.0 - effective_road_risk
    
    # 2. Impact Calculation (Weighted)
    impacts: Dict[str, float] = {
        "crime":       float(round(WEIGHTS["crime"]       * crime_safety_norm * 100.0, 1)),
        "cctv":        float(round(WEIGHTS["cctv"]        * cctv_norm         * 100.0, 1)),
        "lighting":    float(round(WEIGHTS["lighting"]    * lighting_norm     * 100.0, 1)),
        "familiarity": float(round(WEIGHTS["familiarity"] * fam_norm          * 100.0, 1)),
        "road_type":   float(round(WEIGHTS["road_type"]   * road_type_norm    * 100.0, 1)),
    }
    
    total_score = sum(impacts.values())
    final_score = float(max(0.0, min(100.0, round(total_score, 1))))
    
    impacts["time"] = float(round(float((time_mult - 1.0) * (base_density + road_risk) * 10.0), 1) * -1)

    return final_score, impacts

def get_safety_color(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    if score >= 40:
        return "orange"
    return "red"

def get_unsafe_reasons(segment: dict, safety: float) -> list[str]:
    reasons = []
    if segment.get("cctv_count", 0) == 0:
        reasons.append("No CCTV surveillance.")
    if not segment.get("safe_zone_flag", False):
        reasons.append("Few shops or safe zones nearby.")
    return reasons
