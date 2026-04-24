const api = typeof browser !== "undefined" ? browser : chrome;
const sessionId = Math.random().toString(36).substring(2, 15);
const normalizedHost = (window.location.hostname || "browser")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "") || "browser";
const liveUserId = `live_${normalizedHost}`;
let clickTimes = [];
let lastScrollPos = window.scrollY;
let scrollDist = 0;
let startTime = Date.now();
let tabSwitches = 0;
let trustAlertHost;

function ensureAlertHost() {
    if (trustAlertHost && document.body.contains(trustAlertHost)) {
        return trustAlertHost;
    }

    trustAlertHost = document.createElement('div');
    trustAlertHost.id = 'trustcore-alert-host';
    trustAlertHost.style.position = 'fixed';
    trustAlertHost.style.top = '20px';
    trustAlertHost.style.right = '20px';
    trustAlertHost.style.zIndex = '2147483647';
    trustAlertHost.style.display = 'grid';
    trustAlertHost.style.gap = '12px';
    trustAlertHost.style.maxWidth = '360px';
    document.documentElement.appendChild(trustAlertHost);
    return trustAlertHost;
}

function showTrustAlert(alert) {
    const host = ensureAlertHost();
    const card = document.createElement('div');
    const isDanger = alert.severity === 'danger';

    card.style.background = isDanger
        ? 'linear-gradient(135deg, rgba(127, 29, 29, 0.96), rgba(220, 38, 38, 0.96))'
        : 'linear-gradient(135deg, rgba(120, 53, 15, 0.96), rgba(245, 158, 11, 0.96))';
    card.style.color = '#fff';
    card.style.padding = '16px 18px';
    card.style.borderRadius = '18px';
    card.style.boxShadow = '0 20px 50px rgba(15, 23, 42, 0.35)';
    card.style.border = '1px solid rgba(255, 255, 255, 0.18)';
    card.style.fontFamily = 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
    card.style.lineHeight = '1.5';
    card.style.transform = 'translateY(-12px)';
    card.style.opacity = '0';
    card.style.transition = 'opacity 180ms ease, transform 180ms ease';
    card.innerHTML = `
        <div style="display:flex;align-items:flex-start;gap:12px;">
            <div style="width:36px;height:36px;border-radius:12px;display:grid;place-items:center;background:rgba(255,255,255,0.14);font-size:18px;">
                ${isDanger ? '!' : '?'}
            </div>
            <div style="flex:1;">
                <div style="font-size:15px;font-weight:700;margin-bottom:4px;">${alert.title}</div>
                <div style="font-size:13px;opacity:0.92;">${alert.message}</div>
                <div style="font-size:12px;opacity:0.84;margin-top:8px;">Status: ${alert.status} • User: ${alert.userId || 'Current session'}</div>
            </div>
            <button type="button" style="background:transparent;border:0;color:#fff;font-size:18px;cursor:pointer;line-height:1;">x</button>
        </div>
    `;

    const closeButton = card.querySelector('button');
    closeButton.addEventListener('click', () => card.remove());

    host.appendChild(card);
    requestAnimationFrame(() => {
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    });

    setTimeout(() => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(-12px)';
        setTimeout(() => card.remove(), 180);
    }, isDanger ? 9000 : 7000);
}

document.addEventListener('click', () => {
    clickTimes.push(Date.now());
});

window.addEventListener('scroll', () => {
    scrollDist += Math.abs(window.scrollY - lastScrollPos);
    lastScrollPos = window.scrollY;
});

window.addEventListener('blur', () => {
    tabSwitches++;
});

function calculateVariance(arr) {
    if (arr.length < 2) return 0;
    const mean = arr.reduce((a, b) => a + b) / arr.length;
    return arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
}

// Robust metric delivery
setInterval(() => {
    const now = Date.now();
    const duration = (now - startTime) / 1000;

    let avgInterval = 2000;
    let variance = 0;

    if (clickTimes.length > 1) {
        let diffs = [];
        for (let i = 1; i < clickTimes.length; i++) {
            diffs.push(clickTimes[i] - clickTimes[i - 1]);
        }
        avgInterval = diffs.reduce((a, b) => a + b, 0) / diffs.length;
        variance = calculateVariance(diffs);
    }

    const metrics = {
        userId: liveUserId,
        sessionId: sessionId,
        avgClickInterval: avgInterval,
        clickVariance: variance,
        scrollSpeed: scrollDist / duration,
        sessionDuration: duration,
        tabSwitchCount: tabSwitches,
        timestamp: new Date().toISOString()
    };

    try {
        api.runtime.sendMessage({ type: 'SENSE_METRICS', data: metrics }, response => {
            if (api.runtime.lastError) {
                console.warn("[TrustCore] Background disconnected. Buffering...");
            }
        });
    } catch (e) {
        console.error("[TrustCore] Failed to send metrics:", e);
    }

    // Reset counters
    scrollDist = 0;
    clickTimes = [];
    tabSwitches = 0;
    startTime = Date.now();
}, 3000); // Send a live update every 3 seconds

api.runtime.onMessage.addListener((message) => {
    if (message.type === 'TRUST_ALERT' && message.data) {
        showTrustAlert(message.data);
    }
});
