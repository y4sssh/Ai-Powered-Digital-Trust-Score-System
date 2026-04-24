const api = typeof browser !== "undefined" ? browser : chrome;

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

setInterval(updateUI, 1000);
updateUI();
