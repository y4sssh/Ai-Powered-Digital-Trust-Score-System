const api = typeof browser !== "undefined" ? browser : chrome;
const DEFAULT_BACKEND_BASE_URL = "http://localhost:8000";

function normalizeBackendBaseUrl(url) {
    return (url || DEFAULT_BACKEND_BASE_URL).trim().replace(/\/+$/, "");
}

function updateUI() {
    api.storage.local.get(['currentScore'], (result) => {
        if (result.currentScore) {
            const score = result.currentScore.score;
            const status = result.currentScore.status;
            const scoreEl = document.getElementById('score');
            const statusEl = document.getElementById('status');

            scoreEl.textContent = Math.round(score);
            statusEl.textContent = status;

            // Update colors
            if (score > 70) {
                scoreEl.style.borderColor = "#10b981";
                scoreEl.style.boxShadow = "0 0 20px rgba(16, 185, 129, 0.5)";
                statusEl.className = "status status-normal";
            } else if (score > 40) {
                scoreEl.style.borderColor = "#f59e0b";
                scoreEl.style.boxShadow = "0 0 20px rgba(245, 158, 11, 0.5)";
                statusEl.className = "status status-suspicious";
            } else {
                scoreEl.style.borderColor = "#ef4444";
                scoreEl.style.boxShadow = "0 0 20px rgba(239, 68, 68, 0.5)";
                statusEl.className = "status status-risk";
            }
        }
    });
}

function loadBackendUrl() {
    api.storage.local.get({ backendBaseUrl: DEFAULT_BACKEND_BASE_URL }, (result) => {
        document.getElementById('backend-url').value = normalizeBackendBaseUrl(result.backendBaseUrl);
    });
}

function showStatus(message) {
    document.getElementById('config-status').textContent = message;
}

document.getElementById('save-backend-url').addEventListener('click', () => {
    const backendUrl = normalizeBackendBaseUrl(document.getElementById('backend-url').value);
    api.storage.local.set({ backendBaseUrl: backendUrl }, () => {
        showStatus(`Saved: ${backendUrl}`);
    });
});

setInterval(updateUI, 1000);
updateUI();
loadBackendUrl();
