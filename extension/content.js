const api = typeof browser !== "undefined" ? browser : chrome;
const sessionId = Math.random().toString(36).substring(2, 15);
let clickTimes = [];
let lastScrollPos = window.scrollY;
let scrollDist = 0;
let startTime = Date.now();
let tabSwitches = 0;

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
        userId: "demo_user_alpha", // In a real app, this would be fetched from storage/session
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
}, 8000); // Slightly faster interval for demo responsiveness
