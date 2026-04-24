#!/usr/bin/env python3
"""Generate a comprehensive college presentation PDF for AI Trust Scorer."""

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap');
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Inter', sans-serif; background: #fff; color: #1e293b; }

  .cover { background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%);
    color: #fff; min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center;
    padding: 60px 40px; page-break-after: always; }
  .cover .badge { background: rgba(59,130,246,0.2); border: 1px solid rgba(59,130,246,0.5);
    color: #60a5fa; padding: 8px 20px; border-radius: 100px; font-size: 12px;
    font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 32px; }
  .cover h1 { font-size: 52px; font-weight: 900; line-height: 1.1; margin-bottom: 16px;
    background: linear-gradient(135deg, #fff, #93c5fd); -webkit-background-clip: text;
    -webkit-text-fill-color: transparent; }
  .cover .subtitle { font-size: 20px; opacity: 0.7; margin-bottom: 48px; }
  .cover .meta-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 20px;
    width: 100%; max-width: 600px; }
  .cover .meta-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 20px; }
  .cover .meta-box .label { font-size: 11px; opacity: 0.5; text-transform: uppercase;
    letter-spacing: 1px; margin-bottom: 6px; }
  .cover .meta-box .val { font-weight: 700; font-size: 15px; }
  .cover .footer { margin-top: 60px; opacity: 0.4; font-size: 13px; }

  .page { padding: 60px 56px; page-break-after: always; }
  .page:last-child { page-break-after: auto; }

  .section-label { font-size: 11px; font-weight: 700; letter-spacing: 3px;
    text-transform: uppercase; color: #3b82f6; margin-bottom: 8px; }
  .section-title { font-size: 32px; font-weight: 900; color: #0f172a; margin-bottom: 32px;
    padding-bottom: 16px; border-bottom: 3px solid #eff6ff; }

  p { line-height: 1.8; color: #475569; margin-bottom: 12px; font-size: 14px; }

  .toc-item { display: flex; justify-content: space-between; align-items: center;
    padding: 14px 0; border-bottom: 1px solid #f1f5f9; }
  .toc-item .toc-title { font-weight: 600; color: #1e293b; font-size: 15px; }
  .toc-item .toc-page { font-weight: 700; color: #3b82f6; font-size: 13px; }
  .toc-num { font-weight: 700; color: #94a3b8; margin-right: 12px; font-size: 13px; }

  .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 28px; }
  .info-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 22px; }
  .info-card h4 { font-weight: 700; color: #0f172a; margin-bottom: 10px; font-size: 14px; }
  .info-card p { font-size: 13px; margin: 0; }

  .arch-box { background: linear-gradient(135deg, #eff6ff, #f0fdf4);
    border: 1px solid #bfdbfe; border-radius: 16px; padding: 28px; }
  .arch-layer { margin-bottom: 16px; padding: 16px 20px; border-radius: 10px;
    display: flex; align-items: center; gap: 16px; }
  .arch-layer.blue { background: rgba(59,130,246,0.1); border-left: 4px solid #3b82f6; }
  .arch-layer.green { background: rgba(16,185,129,0.1); border-left: 4px solid #10b981; }
  .arch-layer.purple { background: rgba(139,92,246,0.1); border-left: 4px solid #8b5cf6; }
  .arch-layer.orange { background: rgba(245,158,11,0.1); border-left: 4px solid #f59e0b; }
  .arch-layer .icon { font-size: 24px; min-width: 36px; }
  .arch-layer h4 { font-weight: 700; color: #0f172a; font-size: 14px; }
  .arch-layer p { font-size: 12px; margin: 0; color: #64748b; }

  .tech-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; }
  .tech-chip { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 18px; text-align: center; }
  .tech-chip .name { font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 4px; }
  .tech-chip .role { font-size: 12px; color: #64748b; }

  .flow-steps { counter-reset: step; }
  .flow-step { display: flex; gap: 16px; margin-bottom: 20px; align-items: flex-start; }
  .flow-step .step-num { background: #3b82f6; color: #fff; font-weight: 900;
    font-size: 13px; border-radius: 50%; width: 30px; height: 30px; min-width: 30px;
    display: flex; align-items: center; justify-content: center; }
  .flow-step .step-body h4 { font-weight: 700; color: #0f172a; font-size: 14px; margin-bottom: 4px; }
  .flow-step .step-body p { font-size: 13px; margin: 0; }

  pre { background: #0f172a; color: #e2e8f0; border-radius: 12px; padding: 24px;
    font-family: 'JetBrains Mono', monospace; font-size: 11.5px; line-height: 1.7;
    overflow: hidden; margin-bottom: 24px; white-space: pre-wrap; word-break: break-all; }
  .code-label { background: #1e293b; color: #60a5fa; font-family: 'JetBrains Mono', monospace;
    font-size: 11px; font-weight: 700; padding: 6px 16px; border-radius: 8px 8px 0 0;
    display: inline-block; margin-bottom: -2px; }

  .kw { color: #c084fc; }
  .fn { color: #60a5fa; }
  .str { color: #86efac; }
  .cm { color: #475569; font-style: italic; }
  .num { color: #fb923c; }

  .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  .feature-card { border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; }
  .feature-card .icon { font-size: 28px; margin-bottom: 10px; }
  .feature-card h4 { font-weight: 700; font-size: 14px; color: #0f172a; margin-bottom: 6px; }
  .feature-card p { font-size: 13px; margin: 0; }

  .api-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .api-table th { background: #0f172a; color: #fff; padding: 12px 16px; text-align: left;
    font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }
  .api-table td { padding: 12px 16px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }
  .api-table tr:nth-child(even) td { background: #f8fafc; }
  .method { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700;
    padding: 3px 8px; border-radius: 6px; }
  .get { background: #dcfce7; color: #15803d; }
  .post { background: #dbeafe; color: #1d4ed8; }
  .ws { background: #ede9fe; color: #6d28d9; }

  .setup-step { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 18px 22px; margin-bottom: 14px; }
  .setup-step h4 { font-weight: 700; color: #0f172a; font-size: 14px; margin-bottom: 8px; }
  pre.cmd { background: #0f172a; color: #86efac; font-size: 12px; padding: 12px 16px;
    border-radius: 8px; margin: 8px 0 0; white-space: pre-wrap; }

  .conclusion-box { background: linear-gradient(135deg, #0f172a, #1e3a8a);
    color: #fff; border-radius: 16px; padding: 36px; text-align: center; }
  .conclusion-box h3 { font-size: 24px; font-weight: 900; margin-bottom: 12px; }
  .conclusion-box p { opacity: 0.75; font-size: 14px; color: #fff; }

  .page-num { text-align: right; font-size: 11px; color: #94a3b8; margin-top: 40px;
    padding-top: 16px; border-top: 1px solid #f1f5f9; }
</style>
</head>
<body>

<!-- ============ COVER ============ -->
<div class="cover">
  <div class="badge">&#x1F6E1; AI Security Research Project</div>
  <h1>AI Digital Trust Scorer</h1>
  <p class="subtitle">Real-time Behavioral Anomaly Detection using Machine Learning</p>
  <div class="meta-grid">
    <div class="meta-box"><div class="label">Version</div><div class="val">3.0 Production</div></div>
    <div class="meta-box"><div class="label">Date</div><div class="val">April 2026</div></div>
    <div class="meta-box"><div class="label">Type</div><div class="val">Full-Stack System</div></div>
  </div>
  <div class="footer">TrustCore &mdash; AI-Powered Digital Identity Verification</div>
</div>

<!-- ============ TABLE OF CONTENTS ============ -->
<div class="page">
  <div class="section-label">Navigation</div>
  <div class="section-title">Table of Contents</div>
  <div class="toc-item"><div><span class="toc-num">01</span><span class="toc-title">Project Overview &amp; Objectives</span></div><div class="toc-page">Page 3</div></div>
  <div class="toc-item"><div><span class="toc-num">02</span><span class="toc-title">System Architecture</span></div><div class="toc-page">Page 4</div></div>
  <div class="toc-item"><div><span class="toc-num">03</span><span class="toc-title">Technology Stack</span></div><div class="toc-page">Page 5</div></div>
  <div class="toc-item"><div><span class="toc-num">04</span><span class="toc-title">AI Engine &mdash; Isolation Forest</span></div><div class="toc-page">Page 6</div></div>
  <div class="toc-item"><div><span class="toc-num">05</span><span class="toc-title">Backend API (FastAPI)</span></div><div class="toc-page">Page 7</div></div>
  <div class="toc-item"><div><span class="toc-num">06</span><span class="toc-title">Browser Extension</span></div><div class="toc-page">Page 9</div></div>
  <div class="toc-item"><div><span class="toc-num">07</span><span class="toc-title">Admin Dashboard (Frontend)</span></div><div class="toc-page">Page 11</div></div>
  <div class="toc-item"><div><span class="toc-num">08</span><span class="toc-title">API Reference</span></div><div class="toc-page">Page 12</div></div>
  <div class="toc-item"><div><span class="toc-num">09</span><span class="toc-title">Data Flow &amp; System Lifecycle</span></div><div class="toc-page">Page 13</div></div>
  <div class="toc-item"><div><span class="toc-num">10</span><span class="toc-title">Setup &amp; Deployment Guide</span></div><div class="toc-page">Page 14</div></div>
  <div class="toc-item"><div><span class="toc-num">11</span><span class="toc-title">Key Features &amp; Capabilities</span></div><div class="toc-page">Page 15</div></div>
  <div class="toc-item"><div><span class="toc-num">12</span><span class="toc-title">Conclusion &amp; Future Scope</span></div><div class="toc-page">Page 16</div></div>
  <div class="page-num">AI Trust Scorer &mdash; Project Report</div>
</div>

<!-- ============ OVERVIEW ============ -->
<div class="page">
  <div class="section-label">Section 01</div>
  <div class="section-title">Project Overview &amp; Objectives</div>
  <p>The <strong>AI Digital Trust Scorer</strong> is a forensic-grade, real-time behavioral monitoring platform that detects fraudulent, bot-like, or anomalous user behavior on the web. It uses machine learning to continuously evaluate how users interact with websites and assigns a dynamic Trust Score between 0&ndash;100.</p>
  <p>Unlike traditional CAPTCHA or rule-based fraud detection, this system is <strong>passive and invisible</strong>&mdash;it silently observes natural behavioral patterns such as click timing, scroll speed, and tab-switching frequency, then applies an Isolation Forest model to identify statistical outliers that indicate bots or suspicious actors.</p>
  <div class="info-grid">
    <div class="info-card">
      <h4>&#x1F3AF; Problem Statement</h4>
      <p>Online fraud, bots, and fake accounts cause billions in losses annually. Existing detection is intrusive (CAPTCHAs) or reactive (post-fraud). There is a need for a passive, real-time, AI-driven behavioral trust layer.</p>
    </div>
    <div class="info-card">
      <h4>&#x1F4A1; Our Solution</h4>
      <p>A three-layer system: a browser extension that passively collects behavioral metrics, a FastAPI backend with an Isolation Forest AI engine, and a real-time admin dashboard for threat monitoring.</p>
    </div>
    <div class="info-card">
      <h4>&#x1F4CA; Key Metrics Tracked</h4>
      <p>Average click interval (ms), click timing variance, scroll speed (px/s), tab-switch count, and session duration &mdash; all collected without user knowledge or friction.</p>
    </div>
    <div class="info-card">
      <h4>&#x2705; Expected Outcomes</h4>
      <p>Real-time trust scores (0&ndash;100), anomaly flagging, forensic audit logs, identity profiling, and admin-controlled sensitivity thresholds for enterprise deployment.</p>
    </div>
  </div>
  <div class="page-num">Page 3</div>
</div>

<!-- ============ ARCHITECTURE ============ -->
<div class="page">
  <div class="section-label">Section 02</div>
  <div class="section-title">System Architecture</div>
  <p>The system follows a <strong>3-tier microservice architecture</strong> with real-time WebSocket communication between the backend and the admin dashboard.</p>
  <div class="arch-box">
    <div class="arch-layer blue">
      <div class="icon">&#x1F9E9;</div>
      <div><h4>Layer 1 &mdash; Data Collection (Browser Extension)</h4><p>Chrome/Firefox extension using Manifest V3. Content scripts passively record user interactions (clicks, scrolls, tab switches) every 8 seconds and send to the backend via the background service worker.</p></div>
    </div>
    <div class="arch-layer green">
      <div class="icon">&#x1F916;</div>
      <div><h4>Layer 2 &mdash; AI Engine (Python / Scikit-learn)</h4><p>Isolation Forest model pre-trained on 220 behavioral samples (200 normal, 20 bot patterns). Calculates an anomaly score for each behavioral submission, mapped to a 0&ndash;100 trust scale with dynamic sensitivity adjustment.</p></div>
    </div>
    <div class="arch-layer purple">
      <div class="icon">&#x26A1;</div>
      <div><h4>Layer 3 &mdash; API Gateway (FastAPI + SQLite)</h4><p>REST + WebSocket API built with FastAPI. Persists all behavioral logs and trust scores in SQLite. Broadcasts real-time updates to all connected dashboard clients instantly via WebSocket on every new data ingestion.</p></div>
    </div>
    <div class="arch-layer orange">
      <div class="icon">&#x1F4CA;</div>
      <div><h4>Layer 4 &mdash; Admin Dashboard (HTML/CSS/JS)</h4><p>Single-page forensic dashboard with Chart.js visualizations, live Neural Event Stream, Anomaly Lab, Identity Inspector sidebar, Engine Logs, and an adjustable Neural Sensitivity slider.</p></div>
    </div>
  </div>
  <div class="page-num">Page 4</div>
</div>

<!-- ============ TECH STACK ============ -->
<div class="page">
  <div class="section-label">Section 03</div>
  <div class="section-title">Technology Stack</div>
  <div class="tech-grid">
    <div class="tech-chip"><div class="name">Python 3.11+</div><div class="role">Core backend language</div></div>
    <div class="tech-chip"><div class="name">FastAPI</div><div class="role">REST &amp; WebSocket API</div></div>
    <div class="tech-chip"><div class="name">Uvicorn</div><div class="role">ASGI production server</div></div>
    <div class="tech-chip"><div class="name">Scikit-learn</div><div class="role">Isolation Forest ML model</div></div>
    <div class="tech-chip"><div class="name">NumPy / Pandas</div><div class="role">Numerical computation</div></div>
    <div class="tech-chip"><div class="name">Joblib</div><div class="role">Model serialization</div></div>
    <div class="tech-chip"><div class="name">SQLite 3</div><div class="role">Persistent data store</div></div>
    <div class="tech-chip"><div class="name">Pydantic</div><div class="role">Data validation &amp; schemas</div></div>
    <div class="tech-chip"><div class="name">WebSockets</div><div class="role">Real-time push events</div></div>
    <div class="tech-chip"><div class="name">HTML5 / CSS3 / JS</div><div class="role">Frontend dashboard</div></div>
    <div class="tech-chip"><div class="name">Chart.js</div><div class="role">Live data visualization</div></div>
    <div class="tech-chip"><div class="name">Manifest V3</div><div class="role">Browser extension API</div></div>
  </div>
  <div style="margin-top:28px">
    <div class="section-label">Project Structure</div>
    <div class="code-label">Directory Tree</div>
    <pre>val/
&#x251C;&#x2500;&#x2500; backend/
&#x2502;   &#x251C;&#x2500;&#x2500; main.py          &#x2190; FastAPI app, all REST &amp; WebSocket routes
&#x2502;   &#x2514;&#x2500;&#x2500; ai_logic.py      &#x2190; TrustAI class (Isolation Forest engine)
&#x251C;&#x2500;&#x2500; extension/
&#x2502;   &#x251C;&#x2500;&#x2500; manifest.json    &#x2190; Browser extension config (Manifest V3)
&#x2502;   &#x251C;&#x2500;&#x2500; content.js       &#x2190; Passive behavioral data collector
&#x2502;   &#x251C;&#x2500;&#x2500; background.js    &#x2190; Service worker &amp; API relay
&#x2502;   &#x2514;&#x2500;&#x2500; popup.html/js    &#x2190; Extension popup UI
&#x251C;&#x2500;&#x2500; frontend/
&#x2502;   &#x2514;&#x2500;&#x2500; index.html       &#x2190; Admin dashboard (43KB, single-file SPA)
&#x251C;&#x2500;&#x2500; trust_model.joblib   &#x2190; Pre-trained Isolation Forest model
&#x251C;&#x2500;&#x2500; trust_system.db      &#x2190; SQLite database
&#x251C;&#x2500;&#x2500; seed_data.py         &#x2190; Demo data seeder
&#x2514;&#x2500;&#x2500; run.sh               &#x2190; Startup script</pre>
  </div>
  <div class="page-num">Page 5</div>
</div>

<!-- ============ AI ENGINE ============ -->
<div class="page">
  <div class="section-label">Section 04</div>
  <div class="section-title">AI Engine &mdash; Isolation Forest</div>
  <p>The core intelligence of the system is an <strong>Isolation Forest</strong> &mdash; an unsupervised machine learning algorithm that detects anomalies by isolating observations using random decision trees. Anomalous points (bots) require fewer splits to isolate, yielding a lower anomaly score.</p>
  <p><strong>Input Features:</strong> [avg_click_interval, click_variance, scroll_speed, tab_switch_count]</p>
  <p><strong>Training Data:</strong> 200 normal samples + 20 bot samples generated from realistic behavioral distributions.</p>
  <p><strong>Score Mapping:</strong> The raw decision function score (typically &minus;0.5 to +0.5) is mapped to a 0&ndash;100 Trust Score. Scores above 70 = Normal, 40&ndash;70 = Suspicious, below 40 = High Risk.</p>
  <div class="code-label">backend/ai_logic.py</div>
  <pre><span class="kw">import</span> numpy <span class="kw">as</span> np
<span class="kw">from</span> sklearn.ensemble <span class="kw">import</span> IsolationForest
<span class="kw">import</span> joblib

<span class="kw">class</span> <span class="fn">TrustAI</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.model = IsolationForest(contamination=<span class="num">0.05</span>, random_state=<span class="num">42</span>)
        self.is_trained = <span class="kw">False</span>
        self.sensitivity = <span class="num">0.5</span>   <span class="cm"># 0.0 (lax) to 1.0 (strict)</span>
        self._load_model()

    <span class="kw">def</span> <span class="fn">train_initial</span>(self):
        <span class="cm"># Normal behavior: steady clicks, low variance, moderate scroll</span>
        normal = np.random.normal(
            loc=[<span class="num">800</span>, <span class="num">50</span>, <span class="num">120</span>, <span class="num">1</span>], scale=[<span class="num">150</span>, <span class="num">20</span>, <span class="num">30</span>, <span class="num">0.5</span>], size=(<span class="num">200</span>, <span class="num">4</span>))
        <span class="cm"># Bot behavior: fast clicks, extreme variance, high scroll</span>
        bots = np.random.normal(
            loc=[<span class="num">50</span>, <span class="num">5</span>, <span class="num">2000</span>, <span class="num">10</span>], scale=[<span class="num">10</span>, <span class="num">2</span>, <span class="num">500</span>, <span class="num">5</span>], size=(<span class="num">20</span>, <span class="num">4</span>))
        self.model.fit(np.vstack([normal, bots]))
        self.is_trained = <span class="kw">True</span>
        joblib.dump(self.model, <span class="str">"trust_model.joblib"</span>)

    <span class="kw">def</span> <span class="fn">calculate_trust_score</span>(self, behavioral_data):
        data = np.array(behavioral_data).reshape(<span class="num">1</span>, <span class="num">-1</span>)
        raw_score = self.model.decision_function(data)[<span class="num">0</span>]
        <span class="cm"># Adjust for sensitivity setting</span>
        offset = (self.sensitivity - <span class="num">0.5</span>) * <span class="num">0.2</span>
        adjusted = raw_score - offset
        <span class="kw">if</span> adjusted &gt;= <span class="num">0</span>:
            score = <span class="num">70</span> + (adjusted * <span class="num">200</span>)   <span class="cm"># Maps to 70-100</span>
        <span class="kw">else</span>:
            score = <span class="num">70</span> + (adjusted * <span class="num">180</span>)   <span class="cm"># Maps to 0-70</span>
        <span class="kw">return</span> float(np.clip(score, <span class="num">0</span>, <span class="num">100</span>))

ai_engine = <span class="fn">TrustAI</span>()</pre>
  <div class="page-num">Page 6</div>
</div>

<!-- ============ BACKEND ============ -->
<div class="page">
  <div class="section-label">Section 05</div>
  <div class="section-title">Backend API &mdash; FastAPI</div>
  <p>The backend is built with <strong>FastAPI</strong>, a modern high-performance Python web framework. It serves both REST endpoints and a WebSocket channel for real-time event broadcasting to connected dashboard clients.</p>
  <div class="code-label">backend/main.py &mdash; App Setup &amp; WebSocket Manager</div>
  <pre><span class="kw">from</span> fastapi <span class="kw">import</span> FastAPI, WebSocket, WebSocketDisconnect, Body
<span class="kw">from</span> fastapi.middleware.cors <span class="kw">import</span> CORSMiddleware
<span class="kw">from</span> pydantic <span class="kw">import</span> BaseModel

app = <span class="fn">FastAPI</span>(title=<span class="str">"Digital Trust Score API"</span>)
app.add_middleware(CORSMiddleware, allow_origins=[<span class="str">"*"</span>],
                   allow_methods=[<span class="str">"*"</span>], allow_headers=[<span class="str">"*"</span>])

<span class="kw">class</span> <span class="fn">ConnectionManager</span>:
    <span class="kw">def</span> <span class="fn">__init__</span>(self):
        self.active_connections = []

    <span class="kw">async def</span> <span class="fn">connect</span>(self, websocket):
        <span class="kw">await</span> websocket.accept()
        self.active_connections.append(websocket)

    <span class="kw">async def</span> <span class="fn">broadcast</span>(self, message: dict):
        <span class="kw">for</span> conn <span class="kw">in</span> self.active_connections:
            <span class="kw">try</span>: <span class="kw">await</span> conn.send_json(message)
            <span class="kw">except</span>: <span class="kw">pass</span>

manager = <span class="fn">ConnectionManager</span>()</pre>
  <div class="code-label">backend/main.py &mdash; Core Data Collection Endpoint</div>
  <pre><span class="kw">class</span> <span class="fn">BehavioralData</span>(BaseModel):
    userId: str;  sessionId: str = <span class="str">"unknown"</span>;  browser: str = <span class="str">"Chrome"</span>
    avgClickInterval: float;  clickVariance: float
    scrollSpeed: float;  sessionDuration: float;  tabSwitchCount: float

<span class="kw">@app.post</span>(<span class="str">"/api/collect"</span>)
<span class="kw">async def</span> <span class="fn">collect_data</span>(data: BehavioralData):
    <span class="cm"># 1. Persist raw behavioral log to SQLite</span>
    conn = sqlite3.connect(<span class="str">'trust_system.db'</span>)
    conn.execute(<span class="str">"INSERT INTO behavioral_logs VALUES (?,?,?,?,?,?,?,?,?)"</span>,
                 (data.userId, data.browser, data.avgClickInterval,
                  data.clickVariance, data.scrollSpeed,
                  data.sessionDuration, data.tabSwitchCount,
                  time.ctime(), data.sessionId))

    <span class="cm"># 2. Run AI inference</span>
    features = [data.avgClickInterval, data.clickVariance,
                data.scrollSpeed, data.tabSwitchCount]
    score = ai_engine.calculate_trust_score(features)

    <span class="cm"># 3. Update trust score in DB</span>
    conn.execute(<span class="str">"INSERT OR REPLACE INTO user_scores VALUES (?,?,?)"</span>,
                 (data.userId, score, time.ctime()))
    conn.commit(); conn.close()

    status = <span class="str">"Normal"</span> <span class="kw">if</span> score &gt; <span class="num">70</span> <span class="kw">else</span> <span class="str">"Suspicious"</span> <span class="kw">if</span> score &gt; <span class="num">40</span> <span class="kw">else</span> <span class="str">"High Risk"</span>

    <span class="cm"># 4. Broadcast via WebSocket to all dashboard clients</span>
    <span class="kw">await</span> manager.broadcast({<span class="str">"type"</span>: <span class="str">"METRIC_UPDATE"</span>, <span class="str">"data"</span>: {
        <span class="str">"userId"</span>: data.userId, <span class="str">"score"</span>: round(score, <span class="num">2</span>),
        <span class="str">"status"</span>: status, <span class="str">"stats"</span>: <span class="kw">await</span> <span class="fn">get_current_stats</span>()
    }})
    <span class="kw">return</span> {<span class="str">"userId"</span>: data.userId, <span class="str">"score"</span>: round(score, <span class="num">2</span>), <span class="str">"status"</span>: status}</pre>
  <div class="page-num">Page 7</div>
</div>

<!-- ============ EXTENSION ============ -->
<div class="page">
  <div class="section-label">Section 06</div>
  <div class="section-title">Browser Extension</div>
  <p>The extension works on <strong>Chrome, Chromium, Edge, and Firefox</strong>. It uses <strong>Manifest V3</strong> architecture with three components: a content script, a background service worker, and a popup UI.</p>
  <div class="code-label">extension/content.js &mdash; Passive Behavioral Collector</div>
  <pre><span class="kw">const</span> sessionId = Math.random().toString(<span class="num">36</span>).substring(<span class="num">2</span>, <span class="num">15</span>);
<span class="kw">let</span> clickTimes = [], scrollDist = <span class="num">0</span>, tabSwitches = <span class="num">0</span>;

<span class="cm">// Passively track user interactions</span>
document.addEventListener(<span class="str">'click'</span>, () =&gt; clickTimes.push(Date.now()));
window.addEventListener(<span class="str">'scroll'</span>, () =&gt; {
    scrollDist += Math.abs(window.scrollY - lastScrollPos);
    lastScrollPos = window.scrollY;
});
window.addEventListener(<span class="str">'blur'</span>, () =&gt; tabSwitches++);

<span class="cm">// Send metrics every 8 seconds</span>
setInterval(() =&gt; {
    <span class="kw">const</span> duration = (Date.now() - startTime) / <span class="num">1000</span>;
    <span class="kw">let</span> avgInterval = <span class="num">2000</span>, variance = <span class="num">0</span>;
    <span class="kw">if</span> (clickTimes.length &gt; <span class="num">1</span>) {
        <span class="kw">const</span> diffs = clickTimes.slice(<span class="num">1</span>).map((t,i) =&gt; t - clickTimes[i]);
        avgInterval = diffs.reduce((a,b) =&gt; a+b) / diffs.length;
        variance = calculateVariance(diffs);
    }
    api.runtime.sendMessage({
        type: <span class="str">'SENSE_METRICS'</span>,
        data: { userId: <span class="str">"demo_user_alpha"</span>, sessionId,
                avgClickInterval: avgInterval, clickVariance: variance,
                scrollSpeed: scrollDist / duration,
                sessionDuration: duration, tabSwitchCount: tabSwitches }
    });
    scrollDist = <span class="num">0</span>; clickTimes = []; tabSwitches = <span class="num">0</span>;
    startTime = Date.now();
}, <span class="num">8000</span>);</pre>
  <div class="code-label">extension/background.js &mdash; Service Worker &amp; API Relay</div>
  <pre><span class="kw">const</span> BACKEND_URL = <span class="str">"http://localhost:8000/api/collect"</span>;

api.runtime.onMessage.addListener((message, sender, sendResponse) =&gt; {
    <span class="kw">if</span> (message.type === <span class="str">'SENSE_METRICS'</span>) {
        fetch(BACKEND_URL, {
            method: <span class="str">'POST'</span>,
            headers: { <span class="str">'Content-Type'</span>: <span class="str">'application/json'</span> },
            body: JSON.stringify(message.data)
        })
        .then(r =&gt; r.json())
        .then(data =&gt; {
            api.storage.local.set({ currentScore: data });
            <span class="cm">// Alert if high risk detected</span>
            <span class="kw">if</span> (data.score &lt; <span class="num">40</span>) {
                api.notifications.create(<span class="str">'high-risk-alert'</span>, {
                    type: <span class="str">'basic'</span>, title: <span class="str">'&#x26A0;&#xFE0F; Security Alert'</span>,
                    message: <span class="str">`High risk! Trust Score: ${data.score}`</span>
                });
            }
        });
    }
});</pre>
  <div class="code-label">extension/manifest.json</div>
  <pre>{
  <span class="str">"manifest_version"</span>: <span class="num">3</span>,
  <span class="str">"name"</span>: <span class="str">"AI Digital Trust Scorer"</span>,
  <span class="str">"version"</span>: <span class="str">"1.0"</span>,
  <span class="str">"permissions"</span>: [<span class="str">"activeTab"</span>, <span class="str">"storage"</span>, <span class="str">"notifications"</span>],
  <span class="str">"background"</span>: { <span class="str">"service_worker"</span>: <span class="str">"background.js"</span> },
  <span class="str">"content_scripts"</span>: [{
    <span class="str">"matches"</span>: [<span class="str">"&lt;all_urls&gt;"</span>],
    <span class="str">"js"</span>: [<span class="str">"content.js"</span>]
  }],
  <span class="str">"host_permissions"</span>: [<span class="str">"*://localhost/*"</span>]
}</pre>
  <div class="page-num">Page 9</div>
</div>

<!-- ============ DASHBOARD ============ -->
<div class="page">
  <div class="section-label">Section 07</div>
  <div class="section-title">Admin Dashboard (Frontend)</div>
  <p>The dashboard is a <strong>single-page application</strong> (43KB) built with vanilla HTML, CSS, and JavaScript. It connects to the backend via both REST polling and WebSocket for real-time updates.</p>
  <div class="feature-grid">
    <div class="feature-card"><div class="icon">&#x26A1;</div><h4>Neural Event Stream</h4><p>Live feed showing every behavioral ingestion event with user ID, trust tag (CLEAN / SUSPECT / HIGH RISK), and score. Polls <code>/api/logs</code> every 3 seconds as fallback.</p></div>
    <div class="feature-card"><div class="icon">&#x1F4C8;</div><h4>Trust Propagation Chart</h4><p>Rolling 20-point line chart showing average network trust score over time. Updates on every API poll cycle using Chart.js.</p></div>
    <div class="feature-card"><div class="icon">&#x1F9EA;</div><h4>Anomaly Lab</h4><p>Table of all flagged identities with risk scores. Admins can verify as Safe or confirm as Threat, triggering an instant feedback loop to the backend.</p></div>
    <div class="feature-card"><div class="icon">&#x1F50D;</div><h4>Identity Inspector</h4><p>Sidebar panel with a behavioral radar chart showing click speed, variance, scroll smoothness, and multi-task index for any selected user identity.</p></div>
    <div class="feature-card"><div class="icon">&#x1F4DD;</div><h4>Engine Logs</h4><p>Raw terminal-style log view of every behavioral ingress event with timestamp, user ID, variance, and interval values. Auto-scrolls with new data.</p></div>
    <div class="feature-card"><div class="icon">&#x1F3A7;</div><h4>Neural Sensitivity Slider</h4><p>Admin-controlled threshold slider (0.0&ndash;1.0) that adjusts the AI engine's anomaly detection strictness in real-time via <code>POST /api/settings</code>.</p></div>
  </div>
  <div class="page-num">Page 11</div>
</div>

<!-- ============ API REFERENCE ============ -->
<div class="page">
  <div class="section-label">Section 08</div>
  <div class="section-title">API Reference</div>
  <table class="api-table">
    <thead><tr><th>Method</th><th>Endpoint</th><th>Description</th><th>Response</th></tr></thead>
    <tbody>
      <tr><td><span class="method post">POST</span></td><td><code>/api/collect</code></td><td>Submit behavioral metrics. Runs AI inference &amp; broadcasts result.</td><td>userId, score, status</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/stats</code></td><td>Get system-wide stats: total users, average score, anomaly count.</td><td>totalUsers, avgScore, anomalies</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/logs</code></td><td>Fetch last 100 behavioral log entries ordered by timestamp.</td><td>Array of log entries</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/anomalies</code></td><td>Get all users with trust score below 50 (flagged identities).</td><td>Array of {userId, score, time}</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/profile/{user_id}</code></td><td>Deep profile: score history, behavioral fingerprint averages.</td><td>userId, score, history, fingerprint</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/settings</code></td><td>Get current AI engine sensitivity value.</td><td>{sensitivity: float}</td></tr>
      <tr><td><span class="method post">POST</span></td><td><code>/api/settings</code></td><td>Update sensitivity (0.0&ndash;1.0). Broadcasts change to all dashboards.</td><td>{status, sensitivity}</td></tr>
      <tr><td><span class="method post">POST</span></td><td><code>/api/feedback</code></td><td>Submit admin label (Safe/Anomaly) for a given user identity.</td><td>{status: "feedback received"}</td></tr>
      <tr><td><span class="method get">GET</span></td><td><code>/api/export</code></td><td>Export all trust scores as downloadable CSV file.</td><td>CSV file download</td></tr>
      <tr><td><span class="method ws">WS</span></td><td><code>/ws</code></td><td>WebSocket connection. Receives METRIC_UPDATE, STATS_UPDATE, SETTINGS_UPDATE events in real-time.</td><td>JSON event stream</td></tr>
    </tbody>
  </table>
  <div class="page-num">Page 12</div>
</div>

<!-- ============ DATA FLOW ============ -->
<div class="page">
  <div class="section-label">Section 09</div>
  <div class="section-title">Data Flow &amp; System Lifecycle</div>
  <div class="flow-steps">
    <div class="flow-step"><div class="step-num">1</div><div class="step-body"><h4>User Browses a Website</h4><p>The browser extension's content script activates on page load. It begins silently recording click timestamps, scroll distance, and tab-switch events &mdash; no user interaction required.</p></div></div>
    <div class="flow-step"><div class="step-num">2</div><div class="step-body"><h4>Metric Aggregation (every 8s)</h4><p>Content script computes avg click interval, timing variance, scroll speed (px/s), and tab switch count. Sends to the background service worker via <code>runtime.sendMessage</code>.</p></div></div>
    <div class="flow-step"><div class="step-num">3</div><div class="step-body"><h4>API Submission</h4><p>Background service worker POSTs the behavioral payload as JSON to <code>POST /api/collect</code> at the FastAPI backend. CORS allows cross-origin requests from the extension.</p></div></div>
    <div class="flow-step"><div class="step-num">4</div><div class="step-body"><h4>AI Engine Inference</h4><p>The TrustAI engine passes the 4-feature vector through the pre-trained Isolation Forest model. The decision function score is mapped to a 0&ndash;100 Trust Score, adjusted by the admin-configured sensitivity level.</p></div></div>
    <div class="flow-step"><div class="step-num">5</div><div class="step-body"><h4>Persistence &amp; Classification</h4><p>Raw behavioral logs stored in <code>behavioral_logs</code> table. Trust score upserted in <code>user_scores</code>. Status classified as Normal (&gt;70), Suspicious (40&ndash;70), or High Risk (&lt;40).</p></div></div>
    <div class="flow-step"><div class="step-num">6</div><div class="step-body"><h4>Real-Time Dashboard Broadcast</h4><p>Backend broadcasts a <code>METRIC_UPDATE</code> WebSocket event to all connected admin dashboard clients instantly. The dashboard updates the Neural Event Stream, stats, and chart without any polling delay.</p></div></div>
    <div class="flow-step"><div class="step-num">7</div><div class="step-body"><h4>Admin Review &amp; Feedback</h4><p>Dashboard admin can inspect any identity, view their behavioral fingerprint radar chart, and submit a feedback label (Safe/Threat). Feedback updates the trust score and broadcasts a <code>STATS_UPDATE</code> event.</p></div></div>
  </div>
  <div class="page-num">Page 13</div>
</div>

<!-- ============ SETUP GUIDE ============ -->
<div class="page">
  <div class="section-label">Section 10</div>
  <div class="section-title">Setup &amp; Deployment Guide</div>
  <div class="setup-step">
    <h4>Step 1 &mdash; Prerequisites</h4>
    <p>Python 3.11+, pip, any modern browser (Chrome / Firefox / Edge)</p>
  </div>
  <div class="setup-step">
    <h4>Step 2 &mdash; Clone &amp; Create Virtual Environment</h4>
    <pre class="cmd">cd /path/to/project
python3 -m venv venv
source venv/bin/activate</pre>
  </div>
  <div class="setup-step">
    <h4>Step 3 &mdash; Install Python Dependencies</h4>
    <pre class="cmd">pip install fastapi "uvicorn[standard]" websockets scikit-learn \
            numpy pandas joblib pydantic</pre>
  </div>
  <div class="setup-step">
    <h4>Step 4 &mdash; Seed Demo Data (Optional)</h4>
    <pre class="cmd">python seed_data.py</pre>
  </div>
  <div class="setup-step">
    <h4>Step 5 &mdash; Start the Backend Server</h4>
    <pre class="cmd">python backend/main.py
# Server starts at: http://localhost:8000
# API docs at:      http://localhost:8000/docs</pre>
  </div>
  <div class="setup-step">
    <h4>Step 6 &mdash; Open the Admin Dashboard</h4>
    <pre class="cmd"># Open in any browser:
file:///path/to/val/frontend/index.html</pre>
  </div>
  <div class="setup-step">
    <h4>Step 7 &mdash; Load the Browser Extension</h4>
    <p><strong>Chrome/Edge:</strong> Go to <code>chrome://extensions</code> &rarr; Enable Developer Mode &rarr; Load Unpacked &rarr; Select the <code>extension/</code> folder.</p>
    <p><strong>Firefox:</strong> Go to <code>about:debugging</code> &rarr; This Firefox &rarr; Load Temporary Add-on &rarr; Select <code>manifest.json</code>.</p>
  </div>
  <div class="page-num">Page 14</div>
</div>

<!-- ============ FEATURES ============ -->
<div class="page">
  <div class="section-label">Section 11</div>
  <div class="section-title">Key Features &amp; Capabilities</div>
  <div class="feature-grid">
    <div class="feature-card"><div class="icon">&#x1F916;</div><h4>Unsupervised ML Detection</h4><p>Uses Isolation Forest &mdash; no labeled training data needed. Learns what "normal" looks like and flags deviations automatically.</p></div>
    <div class="feature-card"><div class="icon">&#x26A1;</div><h4>Real-Time WebSocket Events</h4><p>Dashboard updates in milliseconds via WebSocket push. No page refresh needed. Supports multiple simultaneous admin clients.</p></div>
    <div class="feature-card"><div class="icon">&#x1F6E1;</div><h4>Passive &amp; Non-Intrusive</h4><p>Zero friction for end users. No CAPTCHAs, no pop-ups. The extension runs silently in the background collecting behavioral signals.</p></div>
    <div class="feature-card"><div class="icon">&#x1F4CA;</div><h4>Dynamic Sensitivity Control</h4><p>Admins can tune the AI model's strictness from 0.0 to 1.0 in real-time without restarting any service.</p></div>
    <div class="feature-card"><div class="icon">&#x1F9EC;</div><h4>Behavioral Fingerprinting</h4><p>Each user identity builds a unique behavioral profile over time. The radar chart visualizes their click speed, variance, scroll pattern, and multitasking index.</p></div>
    <div class="feature-card"><div class="icon">&#x1F4C4;</div><h4>CSV Export &amp; Audit Logs</h4><p>One-click export of all trust scores as a CSV report. Full raw engine logs available for forensic analysis and compliance auditing.</p></div>
    <div class="feature-card"><div class="icon">&#x1F310;</div><h4>Cross-Browser Support</h4><p>Works on Chrome, Chromium, Edge, and Firefox via a unified Manifest V3 extension with a browser API compatibility shim.</p></div>
    <div class="feature-card"><div class="icon">&#x1F501;</div><h4>Admin Feedback Loop</h4><p>Admins can label anomalies as Safe or Threat. Safe labels boost trust scores, enabling a semi-supervised correction mechanism.</p></div>
  </div>
  <div class="page-num">Page 15</div>
</div>

<!-- ============ CONCLUSION ============ -->
<div class="page">
  <div class="section-label">Section 12</div>
  <div class="section-title">Conclusion &amp; Future Scope</div>
  <p>The AI Digital Trust Scorer demonstrates how machine learning can be applied to the real-world problem of online fraud detection. By combining passive behavioral biometrics, unsupervised anomaly detection, and real-time monitoring infrastructure, the system provides enterprise-grade identity trust assessment without any user friction.</p>
  <p>This project covers the full software engineering lifecycle: data collection, ML model training and inference, REST/WebSocket API design, database persistence, browser extension development, and a production-quality admin UI &mdash; making it a comprehensive demonstration of a modern AI-powered security system.</p>
  <div style="margin: 28px 0;">
    <div class="section-label">Future Enhancements</div>
    <div class="info-grid">
      <div class="info-card"><h4>&#x1F9E0; Online Learning</h4><p>Retrain the Isolation Forest incrementally with new data, enabling the model to adapt to evolving bot strategies automatically over time.</p></div>
      <div class="info-card"><h4>&#x1F4F1; Mobile SDK</h4><p>Port the behavioral collection layer to iOS and Android native SDKs to extend trust scoring to mobile application users.</p></div>
      <div class="info-card"><h4>&#x1F5C4;&#xFE0F; Distributed Database</h4><p>Replace SQLite with PostgreSQL or TimescaleDB for high-volume production deployments handling millions of sessions per day.</p></div>
      <div class="info-card"><h4>&#x1F511; OAuth Integration</h4><p>Integrate with SSO/OAuth providers so real authenticated user IDs are tied to behavioral profiles, enabling per-account trust tracking.</p></div>
    </div>
  </div>
  <div class="conclusion-box">
    <h3>&#x1F6E1; TrustCore v3.0</h3>
    <p>AI Digital Trust Scorer &mdash; Real-time Behavioral Anomaly Detection</p>
    <p style="margin-top:8px; font-size:12px;">Backend: FastAPI + Python &bull; AI: Isolation Forest &bull; Frontend: Vanilla JS &bull; Extension: Manifest V3</p>
  </div>
  <div class="page-num">Page 16</div>
</div>

</body>
</html>"""

from weasyprint import HTML as WP
import os

output_path = "/home/error/Documents/val/AI_Trust_Scorer_Report.pdf"
print("Generating PDF...")
WP(string=HTML).write_pdf(output_path)
size = os.path.getsize(output_path)
print(f"Done! PDF saved to: {output_path} ({size:,} bytes)")
