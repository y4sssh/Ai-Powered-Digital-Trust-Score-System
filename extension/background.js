const api = typeof browser !== "undefined" ? browser : chrome;
const DEFAULT_BACKEND_BASE_URL = "http://localhost:8000";
const BROWSER_NAME = typeof browser !== "undefined" ? "Firefox" : /Edg/.test(navigator.userAgent) ? "Edge" : "Chrome";
const ALERT_COOLDOWN_MS = 30000;
const recentAlerts = new Map();

function normalizeBackendBaseUrl(url) {
    return (url || DEFAULT_BACKEND_BASE_URL).replace(/\/+$/, "");
}

function getBackendCollectUrl(callback) {
    api.storage.local.get({ backendBaseUrl: DEFAULT_BACKEND_BASE_URL }, ({ backendBaseUrl }) => {
        callback(`${normalizeBackendBaseUrl(backendBaseUrl)}/api/collect`);
    });
}

function buildAlertPayload(result) {
    if (!result || result.status === "Normal" || result.score > 70) {
        return null;
    }

    const isHighRisk = result.status === "High Risk" || result.score <= 40;
    return {
        severity: isHighRisk ? "danger" : "warning",
        title: isHighRisk ? "Malicious activity detected" : "Suspicious activity detected",
        message: isHighRisk
            ? `Immediate action recommended. Trust Score: ${Math.round(result.score)}.`
            : `Behavior looks suspicious. Trust Score: ${Math.round(result.score)}.`,
        score: result.score,
        status: result.status
    };
}

function shouldNotify(result) {
    const userId = result?.userId || "unknown-user";
    const severity = result?.status || "unknown-status";
    const key = `${userId}:${severity}`;
    const now = Date.now();
    const lastSent = recentAlerts.get(key) || 0;

    if (now - lastSent < ALERT_COOLDOWN_MS) {
        return false;
    }

    recentAlerts.set(key, now);
    return true;
}

function sendPageAlert(sender, payload) {
    if (!sender?.tab?.id) return;
    api.tabs.sendMessage(sender.tab.id, {
        type: "TRUST_ALERT",
        data: payload
    }, () => {
        if (api.runtime.lastError) {
            console.debug("[TrustCore] Unable to deliver in-page alert:", api.runtime.lastError.message);
        }
    });
}

api.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SENSE_METRICS') {
        sendResponse({ queued: true });
        const payload = { ...message.data, browser: BROWSER_NAME };
        getBackendCollectUrl((backendUrl) => {
            fetch(backendUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            })
                .then(response => response.json())
                .then(data => {
                    api.storage.local.set({ currentScore: data });

                    const alertPayload = buildAlertPayload(data);
                    if (alertPayload && shouldNotify(data)) {
                        api.notifications.create(`trust-alert-${Date.now()}`, {
                            type: 'basic',
                            iconUrl: api.runtime.getURL('icon.svg'),
                            title: alertPayload.title,
                            message: `${alertPayload.message} Status: ${data.status}`,
                            priority: 2
                        });
                        sendPageAlert(sender, {
                            ...alertPayload,
                            userId: data.userId
                        });
                    }
                    console.log("Trust Score Updated:", data.score);
                })
                .catch(err => console.error("Error syncing with trust backend:", err));
        });
    }
});
