/**
 * NETRA TAX - Utility Functions
 * Common helper functions for all pages
 */

// ============================================================================
// AUTH & USER MANAGEMENT
// ============================================================================

/**
 * Get current user from localStorage
 */
function getCurrentUser() {
    const user = localStorage.getItem('currentUser');
    return user ? JSON.parse(user) : null;
}

/**
 * Set current user in localStorage
 */
function setCurrentUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!localStorage.getItem('access_token');
}

/**
 * Require authentication - redirect to login if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'login.html';
    }
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('currentUser');
    window.location.href = 'login.html';
}

// ============================================================================
// FORMATTING & DISPLAY
// ============================================================================

/**
 * Format numbers with commas
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Format percentage
 */
function formatPercent(value, decimals = 1) {
    return (value * 100).toFixed(decimals) + '%';
}

/**
 * Format currency
 */
function formatCurrency(value, currency = 'INR') {
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    });
    return formatter.format(value);
}

/**
 * Format date
 */
function formatDate(date) {
    if (!date) return '-';
    const d = new Date(date);
    return d.toLocaleDateString('en-IN');
}

/**
 * Format time ago (e.g., "2 hours ago")
 */
function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Unknown';
    
    const now = new Date();
    const diff = now - new Date(timestamp);
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
}

/**
 * Get risk level badge HTML
 */
function getRiskLevelBadge(riskLevel) {
    const badges = {
        'HIGH': '<span class="badge badge-danger">🔴 HIGH</span>',
        'MEDIUM': '<span class="badge badge-warning">🟡 MEDIUM</span>',
        'LOW': '<span class="badge badge-success">🟢 LOW</span>',
    };
    return badges[riskLevel] || '<span class="badge">Unknown</span>';
}

/**
 * Get status badge HTML
 */
function getStatusBadge(status) {
    const badges = {
        'active': '<span class="badge badge-success">✓ Active</span>',
        'inactive': '<span class="badge badge-secondary">○ Inactive</span>',
        'pending': '<span class="badge badge-warning">⏳ Pending</span>',
        'flagged': '<span class="badge badge-danger">⚠️ Flagged</span>',
    };
    return badges[status] || `<span class="badge">${status}</span>`;
}

// ============================================================================
// NOTIFICATIONS & MODALS
// ============================================================================

/**
 * Show notification toast
 */
function showNotification(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">✕</button>
        </div>
    `;
    
    // Add styles if not already in CSS
    if (!document.querySelector('style[data-toast-styles]')) {
        const style = document.createElement('style');
        style.setAttribute('data-toast-styles', 'true');
        style.textContent = `
            .toast {
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                border-radius: 4px;
                z-index: 10000;
                animation: slideIn 0.3s ease-out;
            }
            .toast-info { background-color: #3498db; color: white; }
            .toast-success { background-color: #27ae60; color: white; }
            .toast-warning { background-color: #f39c12; color: white; }
            .toast-error { background-color: #e74c3c; color: white; }
            .toast-content { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
            .toast-close { background: none; border: none; color: white; cursor: pointer; font-size: 18px; }
            @keyframes slideIn { from { transform: translateX(400px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(toast);
    
    if (duration > 0) {
        setTimeout(() => toast.remove(), duration);
    }
    
    return toast;
}

/**
 * Show loading spinner
 */
function showSpinner(element = document.body) {
    if (!element) return;
    
    const spinner = document.createElement('div');
    spinner.className = 'spinner-overlay';
    spinner.innerHTML = `
        <div class="spinner">
            <div class="spinner-border"></div>
            <p>Loading...</p>
        </div>
    `;
    
    // Add styles if not already in CSS
    if (!document.querySelector('style[data-spinner-styles]')) {
        const style = document.createElement('style');
        style.setAttribute('data-spinner-styles', 'true');
        style.textContent = `
            .spinner-overlay {
                display: flex;
                justify-content: center;
                align-items: center;
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(255,255,255,0.8);
                z-index: 1000;
                border-radius: inherit;
            }
            .spinner { text-align: center; }
            .spinner-border {
                display: inline-block;
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #114C5A;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        `;
        document.head.appendChild(style);
    }
    
    element.style.position = 'relative';
    element.appendChild(spinner);
}

/**
 * Hide loading spinner
 */
function hideSpinner(element = document.body) {
    const spinner = element.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.remove();
    }
}

/**
 * Show modal dialog
 */
function showModal(title, content, buttons = []) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.id = 'customModal';
    
    const buttonsHTML = buttons.length > 0 ? buttons.map(btn => 
        `<button class="btn ${btn.class || 'btn-primary'}" onclick="${btn.onclick || ''}">${btn.text}</button>`
    ).join('') : '<button class="btn btn-primary" onclick="closeModal()">Close</button>';
    
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-header">
                <h2>${title}</h2>
                <button class="modal-close" onclick="closeModal()">✕</button>
            </div>
            <div class="modal-body">
                ${content}
            </div>
            <div class="modal-footer">
                ${buttonsHTML}
            </div>
        </div>
    `;
    
    // Add styles if not already in CSS
    if (!document.querySelector('style[data-modal-styles]')) {
        const style = document.createElement('style');
        style.setAttribute('data-modal-styles', 'true');
        style.textContent = `
            .modal-overlay {
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 2000;
            }
            .modal-dialog {
                background: white;
                border-radius: 8px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
            }
            .modal-header { padding: 20px; border-bottom: 1px solid #ecf0f1; display: flex; justify-content: space-between; align-items: center; }
            .modal-close { background: none; border: none; font-size: 24px; cursor: pointer; }
            .modal-body { padding: 20px; }
            .modal-footer { padding: 20px; border-top: 1px solid #ecf0f1; display: flex; gap: 10px; justify-content: flex-end; }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
    return modal;
}

/**
 * Close modal
 */
function closeModal() {
    const modal = document.getElementById('customModal');
    if (modal) {
        modal.remove();
    }
}

// ============================================================================
// API HELPER
// ============================================================================

/**
 * Make API call with error handling
 */
async function apiCall(endpoint, options = {}) {
    const baseURL = 'http://localhost:8000/api';
    const url = endpoint.startsWith('http') ? endpoint : `${baseURL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    
    const token = localStorage.getItem('access_token');
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, {
            ...options,
            headers,
        });
        
        if (response.status === 401) {
            // Token expired, redirect to login
            localStorage.removeItem('access_token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || error.message || 'API Error');
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

// ============================================================================
// TABLE UTILITIES
// ============================================================================

/**
 * Create table from data
 */
function createTable(data, columns) {
    if (!data || data.length === 0) {
        return '<p class="text-center">No data available</p>';
    }
    
    let html = '<table class="data-table"><thead><tr>';
    
    columns.forEach(col => {
        html += `<th>${col.label}</th>`;
    });
    
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        columns.forEach(col => {
            const value = col.render ? col.render(row[col.key], row) : row[col.key];
            html += `<td>${value || '-'}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    
    return html;
}

// ============================================================================
// EXPORT UTILITIES
// ============================================================================

/**
 * Export data to CSV
 */
function exportToCSV(data, filename = 'export.csv') {
    if (!data || data.length === 0) {
        alert('No data to export');
        return;
    }
    
    const headers = Object.keys(data[0]);
    let csv = headers.join(',') + '\n';
    
    data.forEach(row => {
        csv += headers.map(h => {
            const value = row[h];
            if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                return `"${value.replace(/"/g, '""')}"`;
            }
            return value;
        }).join(',') + '\n';
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

/**
 * Export data to JSON
 */
function exportToJSON(data, filename = 'export.json') {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
}

// ============================================================================
// VALIDATION UTILITIES
// ============================================================================

/**
 * Validate GSTIN format
 */
function isValidGSTIN(gstin) {
    const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
    return gstinRegex.test(gstin);
}

/**
 * Validate email format
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Validate phone number
 */
function isValidPhone(phone) {
    const phoneRegex = /^[0-9]{10}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
}

// ============================================================================
// INITIALIZATION
// ============================================================================

/**
 * Initialize page on DOM load
 */
document.addEventListener('DOMContentLoaded', () => {
    // Check authentication on all pages except login
    if (window.location.pathname !== '/login.html' && !window.location.pathname.endsWith('login.html')) {
        // Don't force auth check - let each page decide
    }
});
