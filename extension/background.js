const api = typeof browser !== "undefined" ? browser : chrome;
const BACKEND_URL = "http://localhost:8000/api/collect";
const BROWSER_NAME = typeof browser !== "undefined" ? "Firefox" : /Edg/.test(navigator.userAgent) ? "Edge" : "Chrome";

api.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'SENSE_METRICS') {
        const payload = { ...message.data, browser: BROWSER_NAME };
        fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => {
                api.storage.local.set({ currentScore: data });

                // Alert if score is high risk
                if (data.score < 40) {
                    api.notifications.create('high-risk-alert', {
                        type: 'basic',
                        iconUrl: 'popup.html', // Best to use an icon file, but fallback here
                        title: '⚠️ Security Alert',
                        message: `High risk detected! Trust Score: ${data.score}. Status: ${data.status}`,
                        priority: 2
                    });
                }
                console.log("Trust Score Updated:", data.score);
            })
            .catch(err => console.error("Error syncing with trust backend:", err));
    }
});
