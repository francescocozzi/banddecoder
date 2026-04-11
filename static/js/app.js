// Band Decoder Web Interface JavaScript

const API_BASE = '';
let config = null;
let updateInterval = null;
let manualMode = false;
let lastRelayStates = { board1: Array(8).fill(false), board2: Array(8).fill(false) };

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Band Decoder Web Interface initialized');
    loadConfig();
    startAutoUpdate();
});

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const result = await response.json();

        if (result.success) {
            config = result.data;
            console.log('Configuration loaded:', config);
            renderBandTable();
        } else {
            console.error('Failed to load config:', result.error);
        }
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

// Start auto-update
function startAutoUpdate() {
    // Initial update
    updateStatus();

    // Update every second
    updateInterval = setInterval(updateStatus, 1000);
}

// Update system status
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const result = await response.json();

        if (result.success) {
            updateDisplay(result.data);
        } else {
            console.error('Failed to update status:', result.error);
            showSystemError();
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showSystemError();
    }
}

// Update display with new data
function updateDisplay(data) {
    // Sync manual mode from server state
    if (typeof data.manual_mode !== 'undefined' && data.manual_mode !== manualMode) {
        manualMode = data.manual_mode;
        applyManualModeUI();
    }

    // Update Radio 1
    updateRadio(1, data.radio1);

    // Update Radio 2
    updateRadio(2, data.radio2);

    // Update relays
    if (data.relays) {
        lastRelayStates = data.relays;
        updateRelays(data.relays);
    }

    // Update antenna display
    updateAntennaDisplay(data);

    // Update system info
    updateSystemInfo(data.system);

    // Clear error if any
    clearSystemError();
}

// Update radio display
function updateRadio(radioNum, radioData) {
    const bandElement = document.getElementById(`radio${radioNum}Band`);
    const bcdElement = document.getElementById(`radio${radioNum}BCD`);
    const relayElement = document.getElementById(`radio${radioNum}Relay`);
    const updateElement = document.getElementById(`radio${radioNum}Update`);

    if (bandElement) {
        bandElement.textContent = radioData.band || 'N/A';
    }

    if (bcdElement) {
        bcdElement.textContent = radioData.bcd_value || 0;
    }

    if (relayElement) {
        relayElement.textContent = radioData.relay_active !== null ? radioData.relay_active : '-';
    }

    if (updateElement && radioData.last_update > 0) {
        const elapsed = Date.now() / 1000 - radioData.last_update;
        updateElement.textContent = elapsed < 5 ? 'Just now' : `${elapsed.toFixed(0)}s ago`;
    }
}

// Update relay display
function updateRelays(relaysData) {
    // Update Board 1
    updateRelayBoard(1, relaysData.board1);

    // Update Board 2
    updateRelayBoard(2, relaysData.board2);
}

// Update single relay board
function updateRelayBoard(boardNum, relayStates) {
    const container = document.getElementById(`board${boardNum}Relays`);
    if (!container) return;

    const otherBoardStates = boardNum === 1 ? lastRelayStates.board2 : lastRelayStates.board1;
    const bandNames = config ? config.bands.map(b => b.name) : [];
    const numBands = config ? config.bands.length : 8;

    // Create relay items if not exist
    if (container.children.length === 0) {
        relayStates.forEach((state, index) => {
            const relayItem = document.createElement('div');
            relayItem.className = 'relay-item';
            relayItem.id = `board${boardNum}_relay${index}`;
            const bandName = bandNames[index] || `R${index}`;
            relayItem.innerHTML = `
                <div class="relay-number">${index}</div>
                <div class="relay-label">${bandName}</div>
                <div class="relay-status ${state ? 'on' : 'off'}">${state ? 'ON' : 'OFF'}</div>
            `;
            container.appendChild(relayItem);
        });
    }

    // Update all relay items
    relayStates.forEach((state, index) => {
        const relayItem = document.getElementById(`board${boardNum}_relay${index}`);
        if (!relayItem) return;

        const statusElement = relayItem.querySelector('.relay-status');

        // Interlock applies to all 8 relays: relay N on boardA blocked if relay N on boardB is ON
        const isInterlocked = manualMode && (otherBoardStates[index] === true);

        // Update visual state — all 8 relays clickable in manual mode
        relayItem.classList.toggle('active', state);
        relayItem.classList.toggle('manual-clickable', manualMode && !isInterlocked);
        relayItem.classList.toggle('interlock-blocked', isInterlocked);

        if (statusElement) {
            if (isInterlocked) {
                statusElement.textContent = 'LOCK';
                statusElement.className = 'relay-status blocked';
            } else {
                statusElement.textContent = state ? 'ON' : 'OFF';
                statusElement.className = `relay-status ${state ? 'on' : 'off'}`;
            }
        }

        // Set click handler in manual mode — all relays clickable except interlocked
        if (manualMode && !isInterlocked) {
            relayItem.onclick = () => setManualRelay(boardNum, index, !state);
        } else {
            relayItem.onclick = null;
        }
    });
}

// Update antenna display
function updateAntennaDisplay(data) {
    const r1 = data.radio1_antenna || 'A';
    const r2 = data.radio2_antenna || 'A';

    document.getElementById('r1AntA')?.classList.toggle('active', r1 === 'A');
    document.getElementById('r1AntB')?.classList.toggle('active', r1 === 'B');
    document.getElementById('r2AntA')?.classList.toggle('active', r2 === 'A');
    document.getElementById('r2AntB')?.classList.toggle('active', r2 === 'B');
}

// Update system info
function updateSystemInfo(systemData) {
    const statusText = document.getElementById('systemStatusText');
    const uptime = document.getElementById('systemUptime');

    if (statusText) {
        statusText.textContent = systemData.status || 'Unknown';
    }

    if (uptime && systemData.uptime) {
        uptime.textContent = formatUptime(systemData.uptime);
    }
}

// Format uptime
function formatUptime(seconds) {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    let result = '';
    if (days > 0) result += `${days}d `;
    if (hours > 0) result += `${hours}h `;
    if (mins > 0) result += `${mins}m `;
    result += `${secs}s`;

    return result;
}

// Render band configuration table
function renderBandTable() {
    if (!config || !config.bands) return;

    const tbody = document.querySelector('#bandTable tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    config.bands.forEach(band => {
        const row = document.createElement('tr');

        const freqRange = `${band.frequency_range[0]}-${band.frequency_range[1]}`;

        row.innerHTML = `
            <td class="band-name">${band.name}</td>
            <td>${freqRange}</td>
            <td>${band.bcd_code}</td>
            <td>${band.relay_radio1}</td>
            <td>${band.relay_radio2}</td>
        `;

        tbody.appendChild(row);
    });
}

// Load antenna mode options
// Toggle manual mode
async function toggleManualMode() {
    const newMode = !manualMode;
    try {
        const response = await fetch(`${API_BASE}/api/manual/mode`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled: newMode })
        });
        const result = await response.json();
        if (result.success) {
            manualMode = result.manual_mode;
            applyManualModeUI();
        }
    } catch (error) {
        console.error('Error toggling manual mode:', error);
    }
}

// Apply manual mode visual state
function applyManualModeUI() {
    const btn = document.getElementById('manualModeBtn');
    const label = document.getElementById('manualModeLabel');
    const banner = document.getElementById('manualModeBanner');

    if (btn) btn.classList.toggle('active', manualMode);
    if (label) label.textContent = manualMode ? 'MANUAL' : 'AUTO';
    if (banner) banner.style.display = manualMode ? 'block' : 'none';

    // Refresh relay display with current states
    updateRelays(lastRelayStates);
}

// Send manual relay command
async function setManualRelay(board, relay, state) {
    try {
        const response = await fetch(`${API_BASE}/api/manual/relay`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board, relay, state })
        });
        const result = await response.json();
        if (!result.success) {
            console.error('Manual relay error:', result.error);
        }
    } catch (error) {
        console.error('Error sending relay command:', error);
    }
}

// Set antenna for a radio
async function setAntenna(radio, antenna) {
    try {
        const response = await fetch(`${API_BASE}/api/antenna/set`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ radio, antenna })
        });

        const result = await response.json();

        if (result.success) {
            updateAntennaDisplay(result.data);
        } else {
            const msg = document.getElementById('antennaInterlockMsg');
            if (msg) {
                msg.textContent = result.error;
                msg.style.display = 'block';
                setTimeout(() => { msg.style.display = 'none'; }, 3000);
            }
        }
    } catch (error) {
        console.error('Error setting antenna:', error);
    }
}

// Restart system
async function restartSystem() {
    if (!confirm('Are you sure you want to restart the band decoder service?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/system/restart`, {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            showNotification('Restart signal sent', 'success');
        } else {
            showNotification('Failed to restart', 'error');
        }
    } catch (error) {
        console.error('Error restarting system:', error);
        showNotification('Error restarting system', 'error');
    }
}

// Show notification (simple implementation)
function showNotification(message, type) {
    console.log(`[${type.toUpperCase()}] ${message}`);
    // TODO: Implement toast notification
}

// Show system error
function showSystemError() {
    const statusBadge = document.querySelector('.status-badge');
    if (statusBadge) {
        statusBadge.style.background = 'rgba(239, 68, 68, 0.1)';
        statusBadge.style.borderColor = '#ef4444';
        const dot = statusBadge.querySelector('.status-dot');
        if (dot) dot.style.background = '#ef4444';
        const text = statusBadge.querySelector('.status-text');
        if (text) text.textContent = 'Connection Error';
    }
}

// Clear system error
function clearSystemError() {
    const statusBadge = document.querySelector('.status-badge');
    if (statusBadge) {
        statusBadge.style.background = 'rgba(34, 197, 94, 0.1)';
        statusBadge.style.borderColor = '#22c55e';
        const dot = statusBadge.querySelector('.status-dot');
        if (dot) dot.style.background = '#22c55e';
        const text = statusBadge.querySelector('.status-text');
        if (text) text.textContent = 'System Running';
    }
}

// Stop auto-update (cleanup)
function stopAutoUpdate() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    stopAutoUpdate();
});
