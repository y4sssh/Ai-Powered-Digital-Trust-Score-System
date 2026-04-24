from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import time
import json
import sqlite3
import asyncio
import hashlib
import re
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ai_logic import ai_engine

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(PROJECT_ROOT, "trust_system.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)
DEMO_SEED_ENABLED = os.getenv("TRUSTCORE_DEMO_SEED", "false").lower() in {"1", "true", "yes", "on"}

app = FastAPI(title="Digital Trust Score API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
backend_dir = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(PROJECT_ROOT, "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html", status_code=302)

# Rate Limiting
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.blocked_ips = set()
        
    def is_rate_limited(self, ip: str, limit: int = 60, window: int = 60) -> bool:
        if ip in self.blocked_ips:
            return True
        now = time.time()
        self.requests[ip] = [t for t in self.requests[ip] if now - t < window]
        if len(self.requests[ip]) >= limit:
            self.blocked_ips.add(ip)
            return True
        self.requests[ip].append(now)
        return False
        
    def unblock_ip(self, ip: str):
        self.blocked_ips.discard(ip)
        self.requests[ip] = []

rate_limiter = RateLimiter()


def get_db_connection():
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# Database Setup
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_scores 
                 (user_id TEXT PRIMARY KEY, score REAL, last_updated TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS behavioral_logs 
                 (user_id TEXT, browser TEXT, avg_click_interval REAL, click_variance REAL, 
                  scroll_speed REAL, session_duration REAL, tab_switch_count REAL, timestamp TEXT)''')
    
    # Migration: Check for session_id column
    c.execute("PRAGMA table_info(behavioral_logs)")
    columns = [col[1] for col in c.fetchall()]
    if 'session_id' not in columns:
        c.execute("ALTER TABLE behavioral_logs ADD COLUMN session_id TEXT")
        print("Migrated behavioral_logs: added session_id")

    c.execute('''CREATE TABLE IF NOT EXISTS feedback 
                 (session_id TEXT, user_id TEXT, label TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings 
                 (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings VALUES (?, ?)", ('sensitivity', '0.5'))
    
    # Alert rules table
    c.execute('''CREATE TABLE IF NOT EXISTS alert_rules 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, condition TEXT, 
                  threshold REAL, enabled INTEGER, channels TEXT, created_at TEXT)''')
    
    # Alerts history table
    c.execute('''CREATE TABLE IF NOT EXISTS alerts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, rule_id INTEGER, user_id TEXT, 
                  score REAL, message TEXT, channel TEXT, sent INTEGER, created_at TEXT)''')
    
    # Blocked IPs table
    c.execute('''CREATE TABLE IF NOT EXISTS blocked_ips 
                 (ip TEXT PRIMARY KEY, reason TEXT, expires_at TEXT, created_at TEXT)''')
    
    conn.commit()
    conn.close()

init_db()


def seed_demo_data():
    if not DEMO_SEED_ENABLED:
        return

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_scores")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    demo_sessions = [
        {
            "user_id": "demo_analyst_01",
            "browser": "Chrome",
            "avg_interval": 812.0,
            "variance": 48.0,
            "scroll": 132.0,
            "duration": 684.0,
            "tab_switches": 1.0,
            "session_id": "demo-session-001"
        },
        {
            "user_id": "demo_customer_02",
            "browser": "Firefox",
            "avg_interval": 965.0,
            "variance": 58.0,
            "scroll": 104.0,
            "duration": 942.0,
            "tab_switches": 2.0,
            "session_id": "demo-session-002"
        },
        {
            "user_id": "demo_bot_03",
            "browser": "Bot-v1",
            "avg_interval": 43.0,
            "variance": 4.0,
            "scroll": 2140.0,
            "duration": 28.0,
            "tab_switches": 15.0,
            "session_id": "demo-session-003"
        },
        {
            "user_id": "demo_risk_04",
            "browser": "Safari",
            "avg_interval": 180.0,
            "variance": 10.0,
            "scroll": 1180.0,
            "duration": 73.0,
            "tab_switches": 8.0,
            "session_id": "demo-session-004"
        },
        {
            "user_id": "demo_member_05",
            "browser": "Edge",
            "avg_interval": 704.0,
            "variance": 36.0,
            "scroll": 188.0,
            "duration": 521.0,
            "tab_switches": 0.0,
            "session_id": "demo-session-005"
        }
    ]

    for session in demo_sessions:
        event_time = current_timestamp()
        features = [
            session["avg_interval"],
            session["variance"],
            session["scroll"],
            session["tab_switches"]
        ]
        result = ai_engine.calculate_trust_score(features)
        final_score = result.get("final_score", result.get("base_score", 50))

        c.execute(
            "INSERT INTO behavioral_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session["user_id"],
                session["browser"],
                session["avg_interval"],
                session["variance"],
                session["scroll"],
                session["duration"],
                session["tab_switches"],
                event_time,
                session["session_id"]
            )
        )
        c.execute(
            "INSERT OR REPLACE INTO user_scores VALUES (?, ?, ?)",
            (session["user_id"], final_score, event_time)
        )

    conn.commit()
    conn.close()


seed_demo_data()

# Alert Notification System
class AlertSystem:
    def __init__(self):
        self.slack_webhook = None
        self.discord_webhook = None
        self.smtp_config = None
        
    async def send_alert(self, message: str, channel: str, data: dict = None):
        if channel == "slack" and self.slack_webhook:
            await self._send_slack(message, data)
        elif channel == "discord" and self.discord_webhook:
            await self._send_discord(message, data)
        elif channel == "email" and self.smtp_config:
            await self._send_email(message, data)
    
    async def _send_slack(self, message: str, data: dict):
        try:
            import aiohttp
            payload = {
                "text": message,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": "🚨 TrustCore Alert"}
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*User:*\n{data.get('userId', 'N/A')}"},
                            {"type": "mrkdwn", "text": f"*Score:*\n{data.get('score', 'N/A')}"}
                        ]
                    }
                ]
            }
            async with aiohttp.ClientSession() as session:
                await session.post(self.slack_webhook, json=payload)
        except Exception as e:
            print(f"Slack alert failed: {e}")
    
    async def _send_discord(self, message: str, data: dict):
        try:
            import aiohttp
            embed = {
                "title": "🚨 TrustCore Security Alert",
                "color": 0xEF4444,
                "fields": [
                    {"name": "User ID", "value": data.get('userId', 'N/A'), "inline": True},
                    {"name": "Trust Score", "value": str(data.get('score', 'N/A')), "inline": True}
                ]
            }
            payload = {"embeds": [embed]}
            async with aiohttp.ClientSession() as session:
                await session.post(self.discord_webhook, json=payload)
        except Exception as e:
            print(f"Discord alert failed: {e}")
    
    async def _send_email(self, message: str, data: dict):
        try:
            import smtplib
            from email.mime.text import MIMEText
            msg = MIMEText(f"{message}\n\nUser: {data.get('userId')}\nScore: {data.get('score')}")
            msg['Subject'] = 'TrustCore Security Alert'
            msg['From'] = self.smtp_config['from']
            msg['To'] = self.smtp_config['to']
            
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['user'], self.smtp_config['pass'])
                server.send_message(msg)
        except Exception as e:
            print(f"Email alert failed: {e}")
    
    async def check_and_notify(self, user_id: str, score: float, data: dict):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM alert_rules WHERE enabled = 1")
        rules = c.fetchall()
        conn.close()
        
        for rule in rules:
            rule_id, name, condition, threshold, enabled, channels, created_at = rule
            should_alert = False
            
            if condition == "below" and score < threshold:
                should_alert = True
            elif condition == "above" and score > threshold:
                should_alert = True
            
            if should_alert:
                message = f"Alert: {name} - User {user_id} score is {score} ({condition} {threshold})"
                channel_list = json.loads(channels) if channels else ["dashboard"]
                
                for channel in channel_list:
                    await self.send_alert(message, channel, {"userId": user_id, "score": score})
                    
                    conn = get_db_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (None, rule_id, user_id, score, message, channel, 0, current_timestamp()))
                    conn.commit()
                    conn.close()

alert_system = AlertSystem()

class BehavioralData(BaseModel):
    userId: str
    sessionId: Optional[str] = "unknown"
    browser: Optional[str] = "Chrome"
    avgClickInterval: float
    clickVariance: float
    scrollSpeed: float
    sessionDuration: float
    tabSwitchCount: float
    userAgent: Optional[str] = ""
    navigatorProps: Optional[Dict] = {}
    ipAddress: Optional[str] = ""
    geoData: Optional[Dict] = {}
    sessionEvents: Optional[List[Dict]] = []
    previousGeo: Optional[Dict] = {}
    timeSinceLastSession: Optional[float] = 0

class ScoreResponse(BaseModel):
    userId: str
    score: float
    status: str
    breakdown: Optional[Dict] = None

async def get_current_stats():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_scores")
    total_users = c.fetchone()[0]
    c.execute("SELECT AVG(score) FROM user_scores")
    avg_score = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM user_scores WHERE score < 40")
    anomalies = c.fetchone()[0]
    conn.close()
    return {
        "totalUsers": total_users,
        "avgScore": round(avg_score, 1),
        "anomalies": anomalies
    }


@app.get("/healthz")
async def health_check():
    conn = get_db_connection()
    conn.close()
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/collect", response_model=ScoreResponse)
async def collect_data(data: BehavioralData, request: Request):
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if rate_limiter.is_rate_limited(client_ip, limit=100, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Too many requests.")
    
    event_time = current_timestamp()
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check blocked IPs
    c.execute("SELECT * FROM blocked_ips WHERE ip = ?", (data.ipAddress or client_ip,))
    if c.fetchone():
        raise HTTPException(status_code=403, detail="IP blocked")
    
    c.execute("INSERT INTO behavioral_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (data.userId, data.browser, data.avgClickInterval, data.clickVariance, 
               data.scrollSpeed, data.sessionDuration, data.tabSwitchCount, event_time, data.sessionId))
    
    features = [data.avgClickInterval, data.clickVariance, data.scrollSpeed, data.tabSwitchCount]
    
    advanced_checks = {}
    
    if data.navigatorProps or data.userAgent:
        advanced_checks["headless_detection"] = ai_engine.detector.detect_headless(
            data.userAgent or "", data.navigatorProps or {}
        )
    
    if data.ipAddress or data.geoData:
        advanced_checks["ip_reputation"] = ai_engine.detector.check_ip_reputation(
            data.ipAddress or "", data.geoData or {}
        )
    
    if data.sessionEvents:
        advanced_checks["session_replay"] = ai_engine.detector.analyze_session_replay(data.sessionEvents)
    
    if data.geoData and data.previousGeo and data.timeSinceLastSession:
        advanced_checks["impossible_travel"] = ai_engine.detector.detect_impossible_travel(
            data.geoData, data.previousGeo, data.timeSinceLastSession
        )
    
    result = ai_engine.calculate_trust_score(features, advanced_checks)
    final_score = result.get("final_score", result.get("base_score", 50))
    
    c.execute("INSERT OR REPLACE INTO user_scores VALUES (?, ?, ?)",
              (data.userId, final_score, event_time))
    
    c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", 
              ('last_geo_' + data.userId, json.dumps(data.geoData or {})))
    
    conn.commit()
    conn.close()
    
    status = "Normal" if final_score > 70 else "Suspicious" if final_score > 40 else "High Risk"
    
    stats = await get_current_stats()
    await manager.broadcast({
        "type": "METRIC_UPDATE",
        "data": {
            "userId": data.userId,
            "score": round(final_score, 2),
            "status": status,
            "browser": data.browser,
            "sessionId": data.sessionId,
            "variance": data.clickVariance,
            "interval": data.avgClickInterval,
            "scroll": data.scrollSpeed,
            "duration": data.sessionDuration,
            "tabSwitches": data.tabSwitchCount,
            "time": event_time,
            "stats": stats,
            "breakdown": result,
            "geo": data.geoData
        }
    })
    
    # Check and trigger alerts
    await alert_system.check_and_notify(data.userId, final_score, {
        "userId": data.userId,
        "score": final_score,
        "geo": data.geoData,
        "ip": data.ipAddress
    })
    
    return {"userId": data.userId, "score": round(final_score, 2), "status": status, "breakdown": result}

@app.get("/api/stats")
async def get_stats():
    return await get_current_stats()

@app.get("/api/users")
async def get_users(limit: int = 100):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT us.user_id, us.score, us.last_updated,
               bl.browser, bl.avg_click_interval, bl.click_variance,
               bl.scroll_speed, bl.session_duration, bl.tab_switch_count,
               bl.timestamp, bl.session_id
        FROM user_scores us
        LEFT JOIN (
            SELECT b1.user_id, b1.browser, b1.avg_click_interval, b1.click_variance,
                   b1.scroll_speed, b1.session_duration, b1.tab_switch_count,
                   b1.timestamp, b1.session_id
            FROM behavioral_logs b1
            INNER JOIN (
                SELECT user_id, MAX(rowid) AS max_rowid
                FROM behavioral_logs
                GROUP BY user_id
            ) latest ON latest.max_rowid = b1.rowid
        ) bl ON bl.user_id = us.user_id
        ORDER BY us.score ASC, us.rowid DESC
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [{
        "userId": row[0],
        "score": round(row[1], 2) if row[1] is not None else 0,
        "lastUpdated": row[2],
        "browser": row[3] or "Unknown",
        "interval": row[4] or 0,
        "variance": row[5] or 0,
        "scroll": row[6] or 0,
        "duration": row[7] or 0,
        "tabSwitches": row[8] or 0,
        "time": row[9],
        "sessionId": row[10] or "N/A"
    } for row in rows]

@app.get("/api/logs")
async def get_logs():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM behavioral_logs ORDER BY rowid DESC LIMIT 100")
    logs = c.fetchall()
    conn.close()
    return [{"userId": l[0], "browser": l[1], "interval": l[2], "variance": l[3], "scroll": l[4], "duration": l[5], "tabSwitches": l[6], "time": l[7], "sessionId": l[8]} for l in logs]

@app.get("/api/anomalies")
async def get_anomalies():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, score, last_updated FROM user_scores WHERE score < 50 ORDER BY rowid DESC")
    anoms = c.fetchall()
    conn.close()
    return [{"userId": a[0], "score": a[1], "time": a[2]} for a in anoms]

@app.get("/api/profile/{user_id}")
async def get_profile(user_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM behavioral_logs WHERE user_id = ? ORDER BY rowid DESC LIMIT 20", (user_id,))
    logs = c.fetchall()
    
    c.execute("SELECT score FROM user_scores WHERE user_id = ?", (user_id,))
    score_row = c.fetchone()
    score = score_row[0] if score_row else 0
    
    conn.close()
    
    if not logs:
        return {"error": "User not found"}
        
    formatted_logs = [{"interval": l[2], "variance": l[3], "scroll": l[4], "tabSwitches": l[6], "time": l[7]} for l in logs]
    
    # Calculate avg fingerprint
    avg_interval = sum(l[2] for l in logs) / len(logs)
    avg_variance = sum(l[3] for l in logs) / len(logs)
    avg_scroll = sum(l[4] for l in logs) / len(logs)
    avg_tabs = sum(l[6] for l in logs) / len(logs)
    
    return {
        "userId": user_id,
        "score": score,
        "history": formatted_logs,
        "fingerprint": {
            "interval": round(avg_interval, 1),
            "variance": round(avg_variance, 3),
            "scroll": round(avg_scroll, 1),
            "tabs": round(avg_tabs, 1)
        }
    }

@app.get("/api/settings")
async def get_settings():
    return {"sensitivity": ai_engine.sensitivity}

@app.post("/api/settings")
async def update_settings(settings: dict = Body(...)):
    if "sensitivity" in settings:
        level = float(settings["sensitivity"])
        ai_engine.set_sensitivity(level)
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO settings VALUES (?, ?)", ('sensitivity', str(level)))
        conn.commit()
        conn.close()
        
        # Broadcast setting change
        await manager.broadcast({"type": "SETTINGS_UPDATE", "data": {"sensitivity": ai_engine.sensitivity}})
        
        return {"status": "success", "sensitivity": ai_engine.sensitivity}
    raise HTTPException(status_code=400, detail="Invalid settings")

@app.post("/api/feedback")
async def submit_feedback(feedback: dict = Body(...)):
    user_id = feedback.get("userId")
    label = feedback.get("label")
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO feedback VALUES (?, ?, ?, ?)", ("manual", user_id, label, current_timestamp()))
    
    if label == "Safe":
        c.execute("UPDATE user_scores SET score = 85.0 WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    
    # Broadcast update
    stats = await get_current_stats()
    await manager.broadcast({"type": "STATS_UPDATE", "data": stats})
    
    return {"status": "feedback received"}

@app.get("/api/export")
async def export_data():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM user_scores")
    scores = c.fetchall()
    conn.close()
    csv_content = "UserID,TrustScore,LastUpdated\n"
    for row in scores:
        csv_content += f"{row[0]},{row[1]},{row[2]}\n"
    from fastapi.responses import Response
    return Response(content=csv_content, media_type="text/csv", 
                    headers={"Content-Disposition": "attachment; filename=trust_report.csv"})

@app.get("/api/report/pdf")
async def generate_pdf_report():
    from weasyprint import HTML
    import io
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM user_scores")
    total_users = c.fetchone()[0]
    c.execute("SELECT AVG(score) FROM user_scores")
    avg_score = c.fetchone()[0] or 0
    c.execute("SELECT COUNT(*) FROM user_scores WHERE score < 40")
    high_risk = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM user_scores WHERE score >= 40 AND score < 70")
    suspicious = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM user_scores WHERE score >= 70")
    safe = c.fetchone()[0]
    c.execute("SELECT * FROM user_scores ORDER BY score ASC LIMIT 20")
    bottom_20 = c.fetchall()
    conn.close()
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; min-height: 100vh; }}
            .container {{ max-width: 900px; margin: 0 auto; padding: 40px; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .header h1 {{ font-size: 36px; font-weight: 900; background: linear-gradient(135deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
            .header p {{ color: #94a3b8; margin-top: 8px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 40px; }}
            .stat-card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 24px; text-align: center; }}
            .stat-card .value {{ font-size: 42px; font-weight: 900; font-family: 'JetBrains Mono', monospace; }}
            .stat-card .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 8px; }}
            .safe {{ color: #10b981; }}
            .warning {{ color: #f59e0b; }}
            .danger {{ color: #ef4444; }}
            .section {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 24px; margin-bottom: 24px; }}
            .section h2 {{ font-size: 18px; margin-bottom: 16px; color: #60a5fa; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.1); color: #94a3b8; font-size: 11px; text-transform: uppercase; }}
            td {{ padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); font-family: 'JetBrains Mono', monospace; font-size: 13px; }}
            .score-safe {{ color: #10b981; font-weight: 700; }}
            .score-warning {{ color: #f59e0b; font-weight: 700; }}
            .score-danger {{ color: #ef4444; font-weight: 700; }}
            .footer {{ text-align: center; padding: 40px; color: #64748b; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>TrustCore Security Report</h1>
                <p>Generated: {current_timestamp()} | AI-Powered Digital Trust Assessment</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="value">{total_users}</div>
                    <div class="label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="value safe">{avg_score:.1f}</div>
                    <div class="label">Avg Trust Score</div>
                </div>
                <div class="stat-card">
                    <div class="value danger">{high_risk}</div>
                    <div class="label">High Risk</div>
                </div>
                <div class="stat-card">
                    <div class="value warning">{suspicious}</div>
                    <div class="label">Suspicious</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Risk Distribution</h2>
                <div style="display: flex; height: 24px; border-radius: 12px; overflow: hidden; background: rgba(255,255,255,0.1);">
                    <div style="width: {safe/(total_users or 1)*100:.1f}%; background: #10b981;" title="Safe: {safe}"></div>
                    <div style="width: {suspicious/(total_users or 1)*100:.1f}%; background: #f59e0b;" title="Suspicious: {suspicious}"></div>
                    <div style="width: {high_risk/(total_users or 1)*100:.1f}%; background: #ef4444;" title="High Risk: {high_risk}"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 12px; color: #94a3b8;">
                    <span class="safe">Safe: {safe} ({safe/(total_users or 1)*100:.1f}%)</span>
                    <span class="warning">Suspicious: {suspicious} ({suspicious/(total_users or 1)*100:.1f}%)</span>
                    <span class="danger">High Risk: {high_risk} ({high_risk/(total_users or 1)*100:.1f}%)</span>
                </div>
            </div>
            
            <div class="section">
                <h2>Top 20 High-Risk Identities</h2>
                <table>
                    <thead>
                        <tr><th>User ID</th><th>Trust Score</th><th>Status</th><th>Last Updated</th></tr>
                    </thead>
                    <tbody>
                        {''.join(f'''<tr>
                            <td>{row[0]}</td>
                            <td class="{'score-danger' if row[1] < 40 else 'score-warning'}">{row[1]:.1f}</td>
                            <td class="{'score-danger' if row[1] < 40 else 'score-warning'}">{'HIGH RISK' if row[1] < 40 else 'SUSPICIOUS'}</td>
                            <td style="opacity: 0.5;">{row[2]}</td>
                        </tr>''' for row in bottom_20)}
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p>TrustCore v3.0 | AI Digital Trust Scorer | Powered by Isolation Forest ML</p>
            </div>
        </div>
    </body>
    </html>"""
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    
    from fastapi.responses import Response
    return Response(content=pdf_bytes, media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=trust_security_report.pdf"})

# ===== Alert & Notification APIs =====

@app.get("/api/alerts/rules")
async def get_alert_rules():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM alert_rules ORDER BY id DESC")
    rules = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "condition": r[2], "threshold": r[3], 
             "enabled": bool(r[4]), "channels": json.loads(r[5]) if r[5] else [], "created_at": r[6]} for r in rules]

@app.post("/api/alerts/rules")
async def create_alert_rule(rule: dict = Body(...)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO alert_rules VALUES (?, ?, ?, ?, ?, ?, ?)",
              (None, rule.get("name"), rule.get("condition"), rule.get("threshold"),
               1 if rule.get("enabled", True) else 0, json.dumps(rule.get("channels", [])), current_timestamp()))
    conn.commit()
    rule_id = c.lastrowid
    conn.close()
    return {"status": "created", "id": rule_id}

@app.put("/api/alerts/rules/{rule_id}")
async def update_alert_rule(rule_id: int, rule: dict = Body(...)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE alert_rules SET name=?, condition=?, threshold=?, enabled=?, channels=? WHERE id=?",
              (rule.get("name"), rule.get("condition"), rule.get("threshold"),
               1 if rule.get("enabled", True) else 0, json.dumps(rule.get("channels", [])), rule_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.delete("/api/alerts/rules/{rule_id}")
async def delete_alert_rule(rule_id: int):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM alert_rules WHERE id=?", (rule_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.get("/api/alerts/history")
async def get_alert_history(limit: int = 50):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,))
    alerts = c.fetchall()
    conn.close()
    return [{"id": a[0], "rule_id": a[1], "user_id": a[2], "score": a[3], 
             "message": a[4], "channel": a[5], "sent": bool(a[6]), "time": a[7]} for a in alerts]

# Webhook Configuration
@app.post("/api/alerts/webhook")
async def configure_webhook(config: dict = Body(...)):
    if config.get("slack"):
        alert_system.slack_webhook = config["slack"]
    if config.get("discord"):
        alert_system.discord_webhook = config["discord"]
    return {"status": "configured", "slack": bool(alert_system.slack_webhook), 
            "discord": bool(alert_system.discord_webhook)}

# Email Configuration
@app.post("/api/alerts/email")
async def configure_email(config: dict = Body(...)):
    alert_system.smtp_config = {
        "host": config.get("host", "smtp.gmail.com"),
        "port": config.get("port", 587),
        "user": config.get("user"),
        "pass": config.get("password"),
        "from": config.get("from"),
        "to": config.get("to")
    }
    return {"status": "configured"}

# IP Blocking
@app.get("/api/blocked-ips")
async def get_blocked_ips():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM blocked_ips")
    ips = c.fetchall()
    conn.close()
    return [{"ip": i[0], "reason": i[1], "expires_at": i[2], "created_at": i[3]} for i in ips]

@app.post("/api/blocked-ips")
async def block_ip(data: dict = Body(...)):
    ip = data.get("ip")
    reason = data.get("reason", "Manual block")
    expires = data.get("expires_at", None)
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO blocked_ips VALUES (?, ?, ?, ?)",
              (ip, reason, expires, current_timestamp()))
    conn.commit()
    conn.close()
    
    rate_limiter.blocked_ips.add(ip)
    return {"status": "blocked", "ip": ip}

@app.delete("/api/blocked-ips/{ip}")
async def unblock_ip(ip: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM blocked_ips WHERE ip=?", (ip,))
    conn.commit()
    conn.close()
    rate_limiter.unblock_ip(ip)
    return {"status": "unblocked", "ip": ip}

# Rate Limit Status
@app.get("/api/rate-limit/status")
async def get_rate_limit_status():
    return {
        "blocked_ips": list(rate_limiter.blocked_ips),
        "active_limited": len(rate_limiter.requests)
    }

@app.post("/api/rate-limit/unblock-all")
async def unblock_all_ips():
    rate_limiter.blocked_ips.clear()
    rate_limiter.requests.clear()
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM blocked_ips")
    conn.commit()
    conn.close()
    return {"status": "all unblocked"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
