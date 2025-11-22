/**
 * NETRA TAX - API Client Utility Module (clean)
 * - Provides APIClient class
 * - Exposes global `api` instance
 * - Auto-detects backend on localhost: tries port 8000 then 5000
 */

class APIClient {
    constructor(baseURL = 'http://localhost:8000/api') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
        this.refreshToken = localStorage.getItem('refresh_token');
    }

    setBaseURL(url) {
        this.baseURL = url.replace(/\/$/, ''); // remove trailing slash
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('access_token', token);
    }

    getHeaders(contentType = 'application/json') {
        const headers = { 'Content-Type': contentType };
        if (this.token) headers['Authorization'] = `Bearer ${this.token}`;
        return headers;
    }

    async request(endpoint, options = {}) {
        // allow full URL endpoints
        const url = endpoint.match(/^https?:\/\//) ? endpoint : `${this.baseURL}${endpoint.startsWith('/') ? '' : '/'}${endpoint}`;
        const defaultOptions = { headers: this.getHeaders(), ...options };

        try {
            const resp = await fetch(url, defaultOptions);
            if (resp.status === 401) {
                // try refresh once
                try { await this.refreshAccessToken(); defaultOptions.headers = this.getHeaders(); } catch (e) { window.location.href = '/login.html'; }
                return fetch(url, defaultOptions).then(r => r.json());
            }
            if (!resp.ok) {
                const errBody = await resp.text().catch(() => null);
                let err = errBody;
                try { err = JSON.parse(errBody); } catch (_) {}
                throw new Error(err && err.detail ? err.detail : `HTTP ${resp.status}: ${resp.statusText}`);
            }
            return await resp.json();
        } catch (e) {
            console.error('API request failed:', e);
            throw e;
        }
    }

    async refreshAccessToken() {
        if (!this.refreshToken) throw new Error('No refresh token');
        const resp = await fetch(`${this.baseURL}/auth/refresh`, { method: 'POST', headers: this.getHeaders(), body: JSON.stringify({ refresh_token: this.refreshToken }) });
        if (!resp.ok) throw new Error('Refresh failed');
        const data = await resp.json();
        this.setToken(data.access_token);
        this.refreshToken = data.refresh_token;
        localStorage.setItem('refresh_token', data.refresh_token);
        return data.access_token;
    }

    // --- Authentication ---
    async login(username, password) { return this.request('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }); }
    async signup(username, email, password, full_name, role = 'analyst') { return this.request('/auth/signup', { method: 'POST', body: JSON.stringify({ username, email, password, full_name, role }) }); }
    async getCurrentUser() { return this.request('/auth/me', { method: 'GET' }); }
    async logout() { return this.request('/auth/logout', { method: 'POST' }); }

    // --- Fraud APIs ---
    async getCompanyRisk(gstin) { return this.request(`/fraud/company/risk?gstin=${encodeURIComponent(gstin)}`, { method: 'GET' }); }
    async analyzeInvoice(invoice_data) { return this.request('/fraud/invoice/risk', { method: 'POST', body: JSON.stringify(invoice_data) }); }
    async getNetworkAnalysis(gstin) { return this.request(`/fraud/network/analysis?gstin=${encodeURIComponent(gstin)}`, { method: 'GET' }); }
    async getFraudRings(node_id) { return this.request(`/fraud/fraud-rings?node_id=${encodeURIComponent(node_id)}`, { method: 'GET' }); }
    async explainFraudPrediction(node_id) { return this.request(`/fraud/explain/${encodeURIComponent(node_id)}`, { method: 'GET' }); }
    async getFraudSummary() { return this.request('/fraud/summary', { method: 'GET' }); }

    // --- File / system / reports ---
    async uploadCSV(file) { const fd = new FormData(); fd.append('file', file); return fetch(`${this.baseURL}/files/upload`, { method: 'POST', headers: { Authorization: `Bearer ${this.token}` }, body: fd }).then(r => r.json()); }
    async buildGraph(upload_id) { return this.request('/files/build-graph', { method: 'POST', body: JSON.stringify({ upload_id }) }); }
    async listUploads(skip = 0, limit = 20) { return this.request(`/files/list?skip=${skip}&limit=${limit}`, { method: 'GET' }); }
    async batchProcess(upload_id) { return this.request('/files/batch-process', { method: 'POST', body: JSON.stringify({ upload_id }) }); }

    async getHealth() { return this.request('/system/health', { method: 'GET' }); }
    async getModelInfo() { return this.request('/system/model-info', { method: 'GET' }); }
    async getConfig() { return this.request('/system/config', { method: 'GET' }); }
    async getStats() { return this.request('/system/stats', { method: 'GET' }); }
    async getLogs(skip = 0, limit = 100) { return this.request(`/system/logs?skip=${skip}&limit=${limit}`, { method: 'GET' }); }

    async generateReport(company_id, report_type = 'comprehensive') { return this.request('/reports/generate', { method: 'POST', body: JSON.stringify({ company_id, report_type }) }); }
    async downloadReport(report_id) { const resp = await fetch(`${this.baseURL}/reports/download/${report_id}`, { headers: { Authorization: `Bearer ${this.token}` } }); if (!resp.ok) throw new Error('Download failed'); return resp.blob(); }
}

// Create global API instance
const api = new APIClient();
window.api = api;

// Backwards compatibility helper for older inline code using apiCall
if (typeof window.apiCall === 'undefined') {
    window.apiCall = async function(endpoint, options = {}) { return api.request(endpoint, options); };
}

// Auto-detect backend baseURL: try port 8000 then 5000. Returns full baseURL like 'http://localhost:8000/api'
async function detectBackendBaseURL(timeoutMs = 2000) {
    const candidates = ['http://localhost:8000/api', 'http://127.0.0.1:8000/api', 'http://localhost:5000/api', 'http://127.0.0.1:5000/api'];
    for (const base of candidates) {
        try {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeoutMs);
            const resp = await fetch(`${base.replace(/\/$/, '')}/fraud/summary`, { signal: controller.signal });
            clearTimeout(id);
            if (resp.ok) {
                return base.replace(/\/$/, '');
            }
        } catch (e) {
            // ignore and try next
        }
    }
    return api.baseURL; // fallback to existing
}

// Run detection on load and set api.baseURL accordingly
(async () => {
    try {
        const detected = await detectBackendBaseURL(1500);
        api.setBaseURL(detected);
        console.info('API base URL set to', detected);
    } catch (e) {
        console.warn('Backend auto-detect failed, using default', api.baseURL);
    }
})();

// --- Small helpers exported for pages ---
function formatNumber(num) { if (num === null || num === undefined) return '0'; return Math.round(num).toLocaleString('en-IN'); }
function formatCurrency(amount) { return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount); }
function formatDate(date) { if (!date) return '-'; return new Date(date).toLocaleDateString('en-IN'); }

// Export a few helpers globally for inline pages
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;

        z-index: 3000;
        animation: slideIn 0.3s ease-in-out;
    `;

    const bgColors = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db',
    };

    notification.style.backgroundColor = bgColors[type];
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease-in-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Show loading spinner
 */
function showSpinner(container) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.innerHTML = `
        <div style="display: flex; justify-content: center; align-items: center; height: 200px;">
            <div style="
                border: 4px solid #f3f3f3;
                border-top: 4px solid #114C5A;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
            "></div>
        </div>
    `;
    container.innerHTML = '';
    container.appendChild(spinner);
}

/**
 * Hide spinner
 */
function hideSpinner() {
    const spinner = document.querySelector('.spinner');
    if (spinner) spinner.remove();
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/login.html';
    }
}

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const userJSON = localStorage.getItem('current_user');
    return userJSON ? JSON.parse(userJSON) : null;
}

/**
 * Set current user in localStorage
 */
function setCurrentUser(user) {
    localStorage.setItem('current_user', JSON.stringify(user));
}

/**
 * Logout user
 */
function logoutUser() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    window.location.href = '/login.html';
}

/**
 * Export functions for global use
 */
window.api = api;
window.showNotification = showNotification;
window.showSpinner = showSpinner;
window.hideSpinner = hideSpinner;
window.formatNumber = formatNumber;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.formatTimeAgo = formatTimeAgo;
window.getRiskLevelBadge = getRiskLevelBadge;
window.validateGSTIN = validateGSTIN;
window.validateEmail = validateEmail;
window.isAuthenticated = isAuthenticated;
window.requireAuth = requireAuth;
window.getCurrentUser = getCurrentUser;
window.setCurrentUser = setCurrentUser;
window.logoutUser = logoutUser;
