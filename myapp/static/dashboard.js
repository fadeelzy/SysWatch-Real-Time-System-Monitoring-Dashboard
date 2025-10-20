// SysWatch Dashboard - Main JavaScript File

// Configuration
const MAX_DATA_POINTS = 20;
const UPDATE_INTERVAL = 3000; // 3 seconds

// Thresholds for alerts
const THRESHOLDS = {
    cpu: { warning: 70, critical: 80 },
    ram: { warning: 75, critical: 85 },
    disk: { warning: 80, critical: 90 },
    ping: { warning: 100, critical: 150 }
};

// Try to extract client ID from URL, e.g. /view/<client_id>
const CLIENT_ID = window.location.pathname.split("/view/")[1] || "demo-client";

// Auto-detect backend base URL
const BASE_URL = `${window.location.origin}/api/metrics/${CLIENT_ID}`;

// Data storage
let metricsData = { cpu: [], ram: [], disk: [], ping: [] };

// Chart instances
let charts = {};

// Chart colors
const COLORS = {
    cpu: { border: '#fb923c', background: 'rgba(251, 146, 60, 0.2)' },
    ram: { border: '#a855f7', background: 'rgba(168, 85, 247, 0.2)' },
    disk: { border: '#22c55e', background: 'rgba(34, 197, 94, 0.2)' },
    ping: { border: '#3b82f6', background: 'rgba(59, 130, 246, 0.2)' }
};

// Initialize when page loads
document.addEventListener("DOMContentLoaded", async function () {
    initializeCharts();
    await fetchHostname();
    startMonitoring();
});

// Fetch client hostname (optional — stored when the agent reports)
async function fetchHostname() {
    try {
        const response = await fetch(`${BASE_URL}/hostname/`);
        if (!response.ok) throw new Error();
        const data = await response.json();
        document.getElementById("hostname").textContent = data.hostname || "Unknown Host";
    } catch (err) {
        document.getElementById("hostname").textContent = "Waiting for agent connection...";
    }
}

// Fetch metric data from backend
async function fetchMetricData(endpoint) {
    const url = `${BASE_URL}/${endpoint}/`;
    try {
        const response = await fetch(url, { cache: "no-cache" });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.value ?? 0;
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return 0;
    }
}

// Initialize charts
function initializeCharts() {
    const chartConfig = {
        cpu: { canvas: 'cpu-chart', color: COLORS.cpu, unit: '%', max: 100 },
        ram: { canvas: 'ram-chart', color: COLORS.ram, unit: '%', max: 100 },
        disk: { canvas: 'disk-chart', color: COLORS.disk, unit: '%', max: 100 },
        ping: { canvas: 'ping-chart', color: COLORS.ping, unit: 'ms', max: null }
    };

    Object.keys(chartConfig).forEach(metric => {
        const config = chartConfig[metric];
        const ctx = document.getElementById(config.canvas).getContext('2d');

        charts[metric] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: metric.toUpperCase(),
                    data: [],
                    borderColor: config.color.border,
                    backgroundColor: config.color.background,
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(17,24,39,0.95)',
                        titleColor: '#fff',
                        bodyColor: '#d1d5db',
                        borderColor: config.color.border,
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: ctx => ctx.parsed.y.toFixed(1) + config.unit
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: '#6b7280', maxTicksLimit: 6, font: { size: 10 } }
                    },
                    y: {
                        min: 0,
                        max: config.max,
                        grid: { color: 'rgba(107,114,128,0.1)' },
                        ticks: {
                            color: '#6b7280',
                            font: { size: 10 },
                            callback: v => v + config.unit
                        }
                    }
                }
            }
        });
    });
}

// Update chart with new data
function updateChart(metric, value) {
    const chart = charts[metric];
    const data = metricsData[metric];
    data.push(value);
    if (data.length > MAX_DATA_POINTS) data.shift();

    const labels = data.map((_, i) => {
        const time = new Date(Date.now() - (data.length - 1 - i) * UPDATE_INTERVAL);
        return time.toLocaleTimeString();
    });

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update('none');

    const unit = metric === 'ping' ? 'ms' : '%';
    document.getElementById(`${metric}-value`).textContent = value.toFixed(1) + unit;
}

// Check alerts
function checkAlerts(metrics) {
    const alerts = [];
    for (const metric in THRESHOLDS) {
        const { warning, critical } = THRESHOLDS[metric];
        const value = metrics[metric];
        const labelMap = { cpu: 'CPU', ram: 'RAM', disk: 'Disk', ping: 'Ping' };
        if (value >= critical) alerts.push({ type: 'critical', metric: labelMap[metric], value, threshold: critical });
        else if (value >= warning) alerts.push({ type: 'warning', metric: labelMap[metric], value, threshold: warning });
    }
    displayAlerts(alerts);
}

// Show alerts
function displayAlerts(alerts) {
    const container = document.getElementById('alert-container');
    if (!container) return;
    if (alerts.length === 0) return container.innerHTML = '';

    container.innerHTML = alerts.map(alert => `
        <div class="alert alert-${alert.type}">
            <div class="alert-content">
                <strong>${alert.type.toUpperCase()}</strong> ${alert.metric} high: ${alert.value.toFixed(1)} (threshold ${alert.threshold})
            </div>
        </div>
    `).join('');
}

// Fetch and update all metrics
async function updateMetrics() {
    try {
        const [cpu, ram, disk, ping] = await Promise.all([
            fetchMetricData('cpu'),
            fetchMetricData('ram'),
            fetchMetricData('disk'),
            fetchMetricData('ping')
        ]);

        updateChart('cpu', cpu);
        updateChart('ram', ram);
        updateChart('disk', disk);
        updateChart('ping', ping);
        checkAlerts({ cpu, ram, disk, ping });
    } catch (error) {
        console.error('Error updating metrics:', error);
    }
}

// Start monitoring
async function startMonitoring() {
    await updateMetrics();
    document.getElementById('loading-spinner').style.display = 'none';
    document.getElementById('charts-grid').style.display = 'grid';
    setInterval(updateMetrics, UPDATE_INTERVAL);
}

// Export for debugging
window.SysWatch = { updateMetrics, THRESHOLDS, metricsData };
