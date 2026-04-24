const api = typeof browser !== "undefined" ? browser : chrome;

// Exporting it for use in other scripts
if (typeof module !== 'undefined') {
    module.exports = api;
} else {
    window.extensionApi = api;
}
