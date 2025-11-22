/**
 * NETRA TAX - Dashboard JavaScript
 * Main dashboard functionality and data loading
 */

// Configuration
const REFRESH_INTERVAL = 30000; // Refresh every 30 seconds
const CHART_COLORS = {
    primary: '#114C5A',
    secondary: '#FFC801',
    danger: '#e74c3c',
    warning: '#f39c12',
    success: '#27ae60',
    info: '#3498db',
};

// Global state
let dashboardState = {
    fraudSummary: null,
    systemHealth: null,
    autoRefresh: true,
    refreshInterval: null,
};

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Dashboard initializing...');
    requireAuth();

    try {
        // Load user info
        await loadUserInfo();

        // Load dashboard data
        await loadDashboardData();

        // Setup event listeners
        setupEventListeners();

        // Setup auto-refresh
        if (dashboardState.autoRefresh) {
            dashboardState.refreshInterval = setInterval(loadDashboardData, REFRESH_INTERVAL);
        }

        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Dashboard initialization error:', error);
        showNotification('Failed to load dashboard', 'error');
    }
});

/**
 * Load current user info and update navbar
 */
async function loadUserInfo() {
    try {
        const user = getCurrentUser();
        if (!user) {
            const response = await api.getCurrentUser();
            setCurrentUser(response);
            updateNavbar(response);
        } else {
            updateNavbar(user);
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
    }
}

/**
 * Update navbar with user information
 */
function updateNavbar(user) {
    const userNameElement = document.querySelector('.user-name');
    const userRoleElement = document.querySelector('.user-role');

    if (userNameElement) userNameElement.textContent = user.full_name || user.username;
    if (userRoleElement) userRoleElement.textContent = user.role.toUpperCase();

    // Update user dropdown
    const userDropdown = document.querySelector('.user-dropdown');
    if (userDropdown) {
        userDropdown.innerHTML = `
            <a href="/profile.html">👤 My Profile</a>
            <a href="/settings.html">⚙️ Settings</a>
            <hr style="margin: 8px 0; border: none; border-top: 1px solid #ecf0f1;">
            <a onclick="logoutUser()" style="cursor: pointer;">🚪 Logout</a>
        `;
    }
}

/**
 * Load all dashboard data
 */
async function loadDashboardData() {
    try {
        // Load fraud summary
        await loadFraudSummary();

        // Load system health
        await loadSystemHealth();

        // Load charts
        await loadCharts();

        // Load alerts
        await loadAlerts();

        // Load high-risk companies
        await loadHighRiskCompanies();

        showNotification('Dashboard updated', 'success', 2000);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Failed to refresh dashboard', 'error');
    }
}

/**
 * Load fraud summary and update metrics
 */
async function loadFraudSummary() {
    try {
        showSpinner(document.querySelector('.metrics-grid'));

        const summary = await api.getFraudSummary();
        dashboardState.fraudSummary = summary;

        // Update metric cards by ID
        document.getElementById('totalEntities').textContent = formatNumber(summary.total_entities);
        document.getElementById('highRiskCount').textContent = formatNumber(summary.high_risk_count);
        document.getElementById('mediumRiskCount').textContent = formatNumber(summary.medium_risk_count);
        document.getElementById('fraudRingCount').textContent = formatNumber(summary.fraud_rings_detected);

        // Update changes
        const highRiskEl = document.getElementById('highRiskCount').parentElement;
        if (highRiskEl && highRiskEl.nextElementSibling) {
            highRiskEl.nextElementSibling.textContent = `${((summary.high_risk_count / summary.total_entities) * 100).toFixed(1)}% of total`;
        }

        const mediumRiskEl = document.getElementById('mediumRiskCount').parentElement;
        if (mediumRiskEl && mediumRiskEl.nextElementSibling) {
            mediumRiskEl.nextElementSibling.textContent = `${((summary.medium_risk_count / summary.total_entities) * 100).toFixed(1)}% of total`;
        }

        const fraudRingEl = document.getElementById('fraudRingCount').parentElement;
        if (fraudRingEl && fraudRingEl.nextElementSibling) {
            fraudRingEl.nextElementSibling.textContent = summary.fraud_rings_detected > 0 ? '⚠️ Immediate action required' : '✓ No active rings';
        }

        hideSpinner();
    } catch (error) {
        console.error('Error loading fraud summary:', error);
        hideSpinner();
        throw error;
    }
}

/**
 * Load system health status
 */
async function loadSystemHealth() {
    try {
        const health = await api.getHealth();
        dashboardState.systemHealth = health;

        // Update health indicators
        const healthIndicator = document.querySelector('.health-indicator');
        if (healthIndicator) {
            if (health.status === 'healthy') {
                healthIndicator.className = 'health-indicator online';
                healthIndicator.style.backgroundColor = '#27ae60';
                document.querySelector('.status').textContent = 'System Online';
            } else {
                healthIndicator.className = 'health-indicator offline';
                healthIndicator.style.backgroundColor = '#e74c3c';
                document.querySelector('.status').textContent = 'System Issues';
            }
        }

        // Update timestamp
        const timestampElement = document.querySelector('.health-timestamp');
        if (timestampElement) {
            timestampElement.textContent = `Last checked: ${formatTimeAgo(health.timestamp)}`;
        }
    } catch (error) {
        console.error('Error loading system health:', error);
        // Don't throw - health check is non-critical
    }
}

/**
 * Load and render charts
 */
async function loadCharts() {
    try {
        const summary = dashboardState.fraudSummary;
        if (!summary) return;

        // Risk distribution pie chart
        renderRiskDistributionChart(summary);

        // Fraud score distribution
        renderFraudScoreDistribution(summary);

        // Trend chart
        renderTrendChart(summary);
    } catch (error) {
        console.error('Error loading charts:', error);
    }
}

/**
 * Render risk distribution pie chart using Plotly
 */
function renderRiskDistributionChart(summary) {
    const container = document.getElementById('riskDistributionChart');
    if (!container) return;

    const high = summary.high_risk_count || 0;
    const medium = summary.medium_risk_count || 0;
    const low = summary.low_risk_count || (summary.total_entities - high - medium);

    const data = [{
        labels: ['High Risk', 'Medium Risk', 'Low Risk'],
        values: [high, medium, low],
        type: 'pie',
        marker: { colors: ['#e74c3c', '#f39c12', '#27ae60'] },
        hoverinfo: 'label+value+percent',
        textposition: 'inside',
        textinfo: 'percent'
    }];

    const layout = {
        height: 300,
        margin: { l: 0, r: 0, t: 20, b: 0 },
        font: { family: 'Arial, sans-serif', color: '#172B36' },
        showlegend: true,
        legend: { orientation: 'v', y: 0.5, x: 1.0 }
    };

    Plotly.newPlot(container, data, layout, { responsive: true });
}

/**
 * Render fraud score distribution using Plotly
 */
function renderFraudScoreDistribution(summary) {
    const container = document.getElementById('fraudScoreChart');
    if (!container) return;

    // Create sample score data based on summary
    const scores = [];
    for (let i = 0; i < summary.high_risk_count; i++) {
        scores.push(0.7 + Math.random() * 0.3);
    }
    for (let i = 0; i < summary.medium_risk_count; i++) {
        scores.push(0.4 + Math.random() * 0.3);
    }
    for (let i = 0; i < summary.low_risk_count; i++) {
        scores.push(Math.random() * 0.4);
    }

    const data = [{
        x: scores,
        type: 'histogram',
        nbinsx: 20,
        marker: { color: '#FF9932', opacity: 0.7 },
        hoverinfo: 'y'
    }];

    const layout = {
        height: 300,
        xaxis: { title: 'Fraud Score', zeroline: false },
        yaxis: { title: 'Number of Entities', zeroline: false },
        margin: { l: 60, r: 40, t: 20, b: 40 },
        font: { family: 'Arial, sans-serif', color: '#172B36' },
        plot_bgcolor: '#f8f9fa',
        paper_bgcolor: '#ffffff'
    };

    Plotly.newPlot(container, data, layout, { responsive: true });
}

/**
 * Render trend chart using Plotly
 */
function renderTrendChart(summary) {
    const container = document.getElementById('trendChart');
    if (!container) return;

    // Generate last 30 days trend
    const days = [];
    const highRiskTrend = [];
    const fraudDetections = [];
    
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }));
        
        // Generate synthetic trend
        const baseHigh = summary.high_risk_count;
        highRiskTrend.push(Math.max(0, baseHigh + Math.floor(Math.random() * 10 - 5)));
        fraudDetections.push(Math.floor(Math.random() * 5 + 1));
    }

    const data = [
        {
            x: days,
            y: highRiskTrend,
            name: 'High-Risk Entities',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#e74c3c', width: 2 },
            marker: { size: 6 }
        },
        {
            x: days,
            y: fraudDetections,
            name: 'New Frauds Detected',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#FFC801', width: 2 },
            marker: { size: 6 },
            yaxis: 'y2'
        }
    ];

    const layout = {
        height: 300,
        xaxis: { title: 'Date' },
        yaxis: { title: 'High-Risk Count', side: 'left' },
        yaxis2: { title: 'New Detections', overlaying: 'y', side: 'right' },
        margin: { l: 60, r: 60, t: 20, b: 40 },
        font: { family: 'Arial, sans-serif', color: '#172B36' },
        plot_bgcolor: '#f8f9fa',
        paper_bgcolor: '#ffffff',
        legend: { x: 0.01, y: 0.99 },
        hovermode: 'x unified'
    };

    Plotly.newPlot(container, data, layout, { responsive: true });
}

    // Draw axes
    ctx.strokeStyle = '#bdc3c7';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.stroke();

    // Draw line
    ctx.strokeStyle = CHART_COLORS.danger;
    ctx.lineWidth = 3;
    ctx.beginPath();

    detectedFrauds.forEach((value, index) => {
        const x = padding + ((width - 2 * padding) / (detectedFrauds.length - 1)) * index;
        const y = height - padding - ((value / maxValue) * (height - 2 * padding));

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    ctx.stroke();

    // Draw points
    ctx.fillStyle = CHART_COLORS.danger;
    detectedFrauds.forEach((value, index) => {
        const x = padding + ((width - 2 * padding) / (detectedFrauds.length - 1)) * index;
        const y = height - padding - ((value / maxValue) * (height - 2 * padding));

        ctx.beginPath();
        ctx.arc(x, y, pointRadius, 0, 2 * Math.PI);
        ctx.fill();
    });

    // Draw labels
    ctx.fillStyle = '#172B36';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'center';

    months.forEach((month, index) => {
        const x = padding + ((width - 2 * padding) / (months.length - 1)) * index;
        ctx.fillText(month, x, height - padding + 20);
    });
}

/**
 * Helper function to draw pie slice
 */
function drawPieSlice(ctx, centerX, centerY, radius, startAngle, endAngle, color) {
    const startAngleRad = (startAngle * Math.PI) / 180;
    const endAngleRad = (endAngle * Math.PI) / 180;

    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, startAngleRad, endAngleRad);
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
}

/**
 * Load alerts
 */
async function loadAlerts() {
    try {
        const alertsContainer = document.querySelector('.alerts-grid');
        if (!alertsContainer) return;

        // Sample alert data - replace with API call when available
        const alerts = [
            {
                title: 'High-Risk Invoice Detected',
                description: 'Invoice INV-2024-001234 flagged as potential fraud',
                time: '2 minutes ago',
                severity: 'high',
            },
            {
                title: 'Unusual Network Pattern',
                description: 'Circular trade pattern detected involving 5 entities',
                time: '15 minutes ago',
                severity: 'high',
            },
            {
                title: 'System Health Check',
                description: 'All systems operational. Last update 30 seconds ago',
                time: '30 seconds ago',
                severity: 'info',
            },
        ];

        alertsContainer.innerHTML = alerts
            .map(
                alert =>
                    `
            <div class="alert-item alert-${alert.severity}">
                <div class="alert-icon">${alert.severity === 'high' ? '⚠️' : 'ℹ️'}</div>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                    <div class="alert-time">${alert.time}</div>
                </div>
            </div>
        `,
            )
            .join('');
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}

/**
 * Load high-risk companies table
 */
async function loadHighRiskCompanies() {
    try {
        const tableBody = document.querySelector('.high-risk-table tbody');
        if (!tableBody) return;

        showSpinner(tableBody.parentElement);

        // For now, load from fraud summary
        const summary = dashboardState.fraudSummary;
        if (!summary || !summary.high_risk_companies) {
            hideSpinner();
            return;
        }

        const rows = summary.high_risk_companies
            .map(
                company => `
            <tr>
                <td>${company.gstin}</td>
                <td>${company.name}</td>
                <td>${company.risk_score.toFixed(2)}</td>
                <td>${getRiskLevelBadge(company.risk_score).level}</td>
                <td>
                    <button class="btn btn-small" onclick="viewCompanyDetails('${company.gstin}')">
                        View Details
                    </button>
                </td>
            </tr>
        `,
            )
            .join('');

        if (rows) {
            tableBody.innerHTML = rows;
        } else {
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No high-risk companies found</td></tr>';
        }

        hideSpinner();
    } catch (error) {
        console.error('Error loading high-risk companies:', error);
        hideSpinner();
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.querySelector('.btn-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadDashboardData();
        });
    }

    // Chart filter dropdowns
    const chartFilters = document.querySelectorAll('.chart-filters select');
    chartFilters.forEach(filter => {
        filter.addEventListener('change', (e) => {
            console.log(`Filter changed: ${e.target.name} = ${e.target.value}`);
            loadCharts();
        });
    });
}

/**
 * View company details
 */
function viewCompanyDetails(gstin) {
    // Navigate to company explorer with GSTIN parameter
    window.location.href = `/company-explorer.html?gstin=${gstin}`;
}

/**
 * Navigate to upload center
 */
function goToUploadCenter() {
    window.location.href = '/upload.html';
}

/**
 * Navigate to graph visualization
 */
function goToGraphVisualization() {
    window.location.href = '/graph-visualizer.html';
}

/**
 * Navigate to reports
 */
function goToReports() {
    window.location.href = '/reports.html';
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (dashboardState.refreshInterval) {
        clearInterval(dashboardState.refreshInterval);
    }
});
