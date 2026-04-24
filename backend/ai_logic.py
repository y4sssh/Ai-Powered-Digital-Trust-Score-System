import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os
import hashlib
import json
from typing import Dict, List, Any

MODEL_PATH = "trust_model.joblib"

class DetectionEngine:
    def __init__(self):
        self.sensitivity = 0.5
        
    def detect_headless(self, user_agent: str, navigator_props: Dict) -> Dict[str, Any]:
        """Detect headless browsers and automation tools"""
        signals = []
        risk_score = 0
        
        ua_lower = user_agent.lower() if user_agent else ""
        
        if "headless" in ua_lower:
            signals.append("Headless UA detected")
            risk_score += 40
        
        if navigator_props.get("webdriver"):
            signals.append("WebDriver detected")
            risk_score += 50
            
        if navigator_props.get("chrome") and not navigator_props.get("permissions"):
            signals.append("Automation flags present")
            risk_score += 20
            
        if navigator_props.get("languages") and "en-US" not in navigator_props.get("languages", []):
            signals.append("Unusual language array")
            risk_score += 10
            
        if navigator_props.get("platform") in ["Linux", "Win32"]:
            if navigator_props.get("hardwareConcurrency", 0) > 16:
                signals.append("Suspicious core count")
                risk_score += 15
                
        return {
            "is_headless": risk_score > 30,
            "signals": signals,
            "risk_score": min(risk_score, 100)
        }
    
    def analyze_session_replay(self, events: List[Dict]) -> Dict[str, Any]:
        """Detect session replay / playback attacks"""
        if not events or len(events) < 2:
            return {"suspicious": False, "reason": "Insufficient data"}
        
        intervals = []
        for i in range(1, min(len(events), 20)):
            prev_time = events[i-1].get("timestamp", 0)
            curr_time = events[i].get("timestamp", 0)
            if curr_time > prev_time:
                intervals.append(curr_time - prev_time)
        
        if not intervals:
            return {"suspicious": False, "reason": "No intervals"}
            
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        signals = []
        risk = 0
        
        if std_interval < 1:
            signals.append("Perfectly uniform timing (scripted)")
            risk += 50
            
        if avg_interval < 5:
            signals.append("Superhuman click speed")
            risk += 40
            
        if max(intervals) - min(intervals) < 0.1:
            signals.append("No timing variation (replay)")
            risk += 45
            
        return {
            "suspicious": risk > 40,
            "signals": signals,
            "risk_score": min(risk, 100),
            "avg_interval_ms": round(avg_interval, 2),
            "std_interval_ms": round(std_interval, 2)
        }
    
    def check_ip_reputation(self, ip: str, geo_data: Dict) -> Dict[str, Any]:
        """Analyze IP reputation and geo-data"""
        risk = 0
        signals = []
        
        if not ip or ip == "127.0.0.1" or ip.startswith("192.168") or ip.startswith("10."):
            signals.append("Private/Local IP")
            risk += 10
            
        if geo_data.get("country") in ["RU", "CN", "KP", "IR", "SY"]:
            signals.append("High-risk country")
            risk += 25
            
        is_vpn = geo_data.get("is_vpn", False) or geo_data.get("is_proxy", False)
        if is_vpn:
            signals.append("VPN/Proxy detected")
            risk += 30
            
        if geo_data.get("is_datacenter", False):
            signals.append("Datacenter IP")
            risk += 35
            
        return {
            "risk_score": min(risk, 100),
            "signals": signals,
            "is_suspicious": risk > 30,
            "country": geo_data.get("country", "Unknown"),
            "city": geo_data.get("city", "Unknown")
        }
    
    def detect_impossible_travel(self, current_geo: Dict, prev_geo: Dict, time_diff_hours: float) -> Dict[str, Any]:
        """Detect impossible travel between login attempts"""
        if not prev_geo or time_diff_hours <= 0:
            return {"impossible": False, "reason": "No previous location"}
            
        lat1, lon1 = current_geo.get("lat", 0), current_geo.get("lon", 0)
        lat2, lon2 = prev_geo.get("lat", 0), prev_geo.get("lon", 0)
        
        distance_km = self._haversine_distance(lat1, lon1, lat2, lon2)
        
        max_physically_possible = time_diff_hours * 1000
        
        is_impossible = distance_km > max_physically_possible
        
        return {
            "impossible": is_impossible,
            "distance_km": round(distance_km, 1),
            "time_hours": round(time_diff_hours, 2),
            "max_possible_km": round(max_physically_possible, 1),
            "signals": ["Impossible travel detected"] if is_impossible else []
        }
    
    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        return R * 2 * np.arcsin(np.sqrt(a))


class TrustAI:
    def __init__(self):
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.is_trained = False
        self.sensitivity = 0.5
        self.detector = DetectionEngine()
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.is_trained = True
            except:
                self.train_initial()

    def train_initial(self):
        # Features: [avg_click_interval, click_variance, scroll_speed, tab_switch_count]
        # Normal data: steady clicks, low variance, moderate scroll
        normal_data = np.random.normal(loc=[800, 50, 120, 1], scale=[150, 20, 30, 0.5], size=(200, 4))
        # Bot data: very fast clicks, extremely high or low variance, high scroll
        bot_data = np.random.normal(loc=[50, 5, 2000, 10], scale=[10, 2, 500, 5], size=(20, 4))
        
        X = np.vstack([normal_data, bot_data])
        self.model.fit(X)
        self.is_trained = True
        joblib.dump(self.model, MODEL_PATH)

    def set_sensitivity(self, level):
        """ level: 0.0 (lax) to 1.0 (strict) """
        self.sensitivity = np.clip(level, 0.0, 1.0)

    def calculate_trust_score(self, behavioral_data, advanced_checks: Dict = None):
        """
        behavioral_data: [avg_click_interval, click_variance, scroll_speed, tab_switch_count]
        advanced_checks: optional dict with ip_reputation, geo_data, headless_detection, session_events
        """
        if not self.is_trained:
            self.train_initial()
        
        data = np.array(behavioral_data).reshape(1, -1)
        raw_score = self.model.decision_function(data)[0]
        
        offset = (self.sensitivity - 0.5) * 0.2
        adjusted_raw = raw_score - offset

        if adjusted_raw >= 0:
            score = 70 + (adjusted_raw * 200)
        else:
            score = 70 + (adjusted_raw * 180)
            
        base_score = float(np.clip(score, 0, 100))
        
        breakdown = {
            "base_score": round(base_score, 1),
            "behavioral_contribution": round(base_score * 0.6, 1),
            "factors": []
        }
        
        if advanced_checks:
            if advanced_checks.get("ip_reputation"):
                ip_risk = advanced_checks["ip_reputation"].get("risk_score", 0)
                if ip_risk > 30:
                    breakdown["factors"].append({
                        "name": "IP Reputation",
                        "risk": ip_risk,
                        "description": advanced_checks["ip_reputation"].get("signals", [])
                    })
                    
            if advanced_checks.get("headless_detection"):
                hl_risk = advanced_checks["headless_detection"].get("risk_score", 0)
                if hl_risk > 0:
                    breakdown["factors"].append({
                        "name": "Headless/Bot Detection",
                        "risk": hl_risk,
                        "description": advanced_checks["headless_detection"].get("signals", [])
                    })
                    
            if advanced_checks.get("session_replay"):
                sr_risk = advanced_checks["session_replay"].get("risk_score", 0)
                if sr_risk > 0:
                    breakdown["factors"].append({
                        "name": "Session Replay",
                        "risk": sr_risk,
                        "description": advanced_checks["session_replay"].get("signals", [])
                    })
                    
            if advanced_checks.get("impossible_travel") and advanced_checks["impossible_travel"].get("impossible"):
                breakdown["factors"].append({
                    "name": "Impossible Travel",
                    "risk": 80,
                    "description": [f"Traveled {advanced_checks['impossible_travel']['distance_km']}km in {advanced_checks['impossible_travel']['time_hours']}h"]
                })
            
            total_risk = sum(f["risk"] for f in breakdown["factors"])
            if total_risk > 0:
                penalty = min(total_risk * 0.4, 40)
                final_score = max(base_score - penalty, 0)
                breakdown["final_score"] = round(final_score, 1)
                breakdown["total_risk_penalty"] = round(penalty, 1)
            else:
                breakdown["final_score"] = round(base_score, 1)
                breakdown["total_risk_penalty"] = 0
        else:
            breakdown["final_score"] = round(base_score, 1)
            breakdown["total_risk_penalty"] = 0
            
        return breakdown

    def feedback_update(self, data, is_anomaly=False):
        # Logic to store feedback for future training
        pass

ai_engine = TrustAI()
