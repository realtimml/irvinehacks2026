// ============================================
// Alarm Clock UI — JavaScript
// Socket.IO integration with Python backend
// ============================================

// Socket.IO connection
const socket = io();

document.addEventListener('DOMContentLoaded', () => {
    initClock();
    initToggles();
    initAddNew();
    initAlarmEdit();
    initNavTabs();
    initModal();
    initSocket();
});

// ============================================
// State
// ============================================
let editingAlarmId = null; // null = adding new, otherwise the alarm ID being edited

// ============================================
// Socket.IO — Backend Communication
// ============================================
function initSocket() {
    // Request initial alarm list from backend
    socket.emit('message', { type: 'get_alarms', data: {} });

    // Receive full alarm list (on load or after changes)
    socket.on('alarms_list', (data) => {
        renderAlarmList(data.alarms || []);
    });

    socket.on('alarm_changed', (data) => {
        renderAlarmList(data.alarms || []);
    });

    // Alarm triggered notification
    socket.on('alarm_triggered', (data) => {
        console.log('🔔 Alarm triggered:', data);
        highlightAlarm(data.id);
    });
}

// ============================================
// Render Alarm List from Backend Data
// ============================================
function renderAlarmList(alarms) {
    const alarmList = document.getElementById('alarm-list');
    if (!alarmList) return;

    alarmList.innerHTML = '';

    alarms.forEach(alarm => {
        const isActive = alarm.enabled;
        const daysStr = alarm.days.length > 0 ? alarm.days.join(', ') : 'No days';

        const row = document.createElement('div');
        row.className = `alarm-row ${isActive ? 'active' : 'inactive'}`;
        row.dataset.alarmId = alarm.id;
        row.innerHTML = `
            <div class="alarm-info">
                <p class="alarm-days">${daysStr}</p>
                <p class="alarm-time">${alarm.time}</p>
            </div>
            <label class="toggle-switch">
                <input type="checkbox" ${isActive ? 'checked' : ''}>
                <span class="toggle-track">
                    <span class="toggle-thumb"></span>
                </span>
            </label>
        `;

        alarmList.appendChild(row);
    });
}

// ============================================
// Highlight an alarm row when it triggers
// ============================================
function highlightAlarm(alarmId) {
    const row = document.querySelector(`.alarm-row[data-alarm-id="${alarmId}"]`);
    if (!row) return;

    row.style.transition = 'box-shadow 0.3s ease, background 0.3s ease';
    row.style.boxShadow = '0 0 20px rgba(255, 180, 0, 0.6)';
    row.style.background = 'rgba(255, 180, 0, 0.15)';

    setTimeout(() => {
        row.style.boxShadow = '';
        row.style.background = '';
    }, 3000);
}

// ============================================
// Live Clock
// ============================================
function initClock() {
    const clockEl = document.getElementById('current-time');
    if (!clockEl) return;

    function updateClock() {
        const now = new Date();
        let hours = now.getHours();
        const minutes = now.getMinutes();
        const ampm = hours >= 12 ? 'PM' : 'AM';
        hours = hours % 12 || 12;

        const hh = String(hours).padStart(2, '0');
        const mm = String(minutes).padStart(2, '0');
        clockEl.textContent = `${hh}:${mm} ${ampm}`;
    }

    updateClock();
    setInterval(updateClock, 1000);
}

// ============================================
// Toggle Switches (delegated) — sends to backend
// ============================================
function initToggles() {
    const alarmList = document.getElementById('alarm-list');
    if (!alarmList) return;

    alarmList.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            const row = e.target.closest('.alarm-row');
            if (!row) return;

            const alarmId = row.dataset.alarmId;
            const enabled = e.target.checked;

            // Update visual state immediately for responsiveness
            if (enabled) {
                row.classList.remove('inactive');
                row.classList.add('active');
            } else {
                row.classList.remove('active');
                row.classList.add('inactive');
            }

            // Send toggle to backend
            socket.emit('message', {
                type: 'toggle_alarm',
                data: { id: parseInt(alarmId), enabled: enabled }
            });
        }
    });
}

// ============================================
// Add New → opens modal in "add" mode
// ============================================
function initAddNew() {
    const addBtn = document.getElementById('add-new-btn');
    if (!addBtn) return;

    addBtn.addEventListener('click', () => {
        openModal(null); // null = new alarm
    });
}

// ============================================
// Click alarm row → opens modal in "edit" mode
// ============================================
function initAlarmEdit() {
    const alarmList = document.getElementById('alarm-list');
    if (!alarmList) return;

    alarmList.addEventListener('click', (e) => {
        // Only open edit if they clicked on the alarm-info area (not the toggle)
        const info = e.target.closest('.alarm-info');
        if (!info) return;

        const row = info.closest('.alarm-row');
        if (!row) return;

        const alarmId = row.dataset.alarmId;
        openModal(alarmId);
    });
}

// ============================================
// Bottom Nav Tabs
// ============================================
function initNavTabs() {
    const navTabs = document.querySelectorAll('.nav-tab');
    navTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            navTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
}

// ============================================
// Modal — Initialization & Logic
// ============================================

// Map between short day keys and display abbreviations
const DAY_ORDER = ['M', 'T', 'W', 'Th', 'F', 'Sa', 'S'];

function initModal() {
    const overlay = document.getElementById('modal-overlay');
    const cancelBtn = document.getElementById('modal-cancel');
    const deleteBtn = document.getElementById('modal-delete');
    const saveBtn = document.getElementById('modal-save');

    // Cancel
    cancelBtn.addEventListener('click', closeModal);

    // Close on overlay click (outside modal)
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeModal();
    });

    // Delete — sends to backend
    deleteBtn.addEventListener('click', () => {
        if (editingAlarmId !== null) {
            socket.emit('message', {
                type: 'delete_alarm',
                data: { id: parseInt(editingAlarmId) }
            });
            closeModal();
        }
    });

    // Save
    saveBtn.addEventListener('click', handleSave);

    // Time picker arrows
    document.querySelectorAll('.picker-arrow').forEach(btn => {
        btn.addEventListener('click', () => {
            const col = btn.dataset.col;
            const dir = btn.dataset.dir;
            adjustPicker(col, dir);
        });
    });

    // Day buttons
    document.querySelectorAll('.day-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.classList.toggle('selected');
        });
    });
}

// ============================================
// Open Modal
// ============================================
function openModal(alarmId) {
    const overlay = document.getElementById('modal-overlay');
    const title = document.getElementById('modal-title');
    const deleteBtn = document.getElementById('modal-delete');

    editingAlarmId = alarmId;

    if (alarmId === null) {
        // --- New alarm mode ---
        title.textContent = 'New Alarm';
        deleteBtn.classList.add('hidden');

        // Default to current time rounded to nearest 15 min
        const now = new Date();
        let h = now.getHours();
        let m = Math.ceil(now.getMinutes() / 15) * 15;
        if (m === 60) { m = 0; h++; }
        const ampm = h >= 12 ? 'PM' : 'AM';
        h = h % 12 || 12;

        setPickerValues(
            String(h).padStart(2, '0'),
            String(m).padStart(2, '0'),
            ampm
        );

        // Clear all day selections
        document.querySelectorAll('.day-btn').forEach(b => b.classList.remove('selected'));
    } else {
        // --- Edit mode ---
        title.textContent = 'Edit Alarm';
        deleteBtn.classList.remove('hidden');

        const row = document.querySelector(`.alarm-row[data-alarm-id="${alarmId}"]`);
        if (!row) return;

        // Parse existing time
        const timeText = row.querySelector('.alarm-time').textContent.trim(); // e.g. "08:00 AM"
        const [timePart, ampm] = timeText.split(' ');
        const [hh, mm] = timePart.split(':');

        setPickerValues(hh, mm, ampm);

        // Parse existing days
        const daysText = row.querySelector('.alarm-days').textContent.trim(); // e.g. "M, W, F"
        const activeDays = daysText.split(',').map(d => d.trim());

        document.querySelectorAll('.day-btn').forEach(b => {
            b.classList.toggle('selected', activeDays.includes(b.dataset.day));
        });
    }

    // Show modal
    overlay.classList.add('open');
}

// ============================================
// Close Modal
// ============================================
function closeModal() {
    const overlay = document.getElementById('modal-overlay');
    overlay.classList.remove('open');
    editingAlarmId = null;
}

// ============================================
// Set Picker Values
// ============================================
function setPickerValues(hh, mm, ampm) {
    document.getElementById('picker-hours-val').textContent = hh;
    document.getElementById('picker-minutes-val').textContent = mm;
    document.getElementById('picker-ampm-val').textContent = ampm;
}

// ============================================
// Adjust Picker (arrow clicks)
// ============================================
function adjustPicker(col, dir) {
    if (col === 'hours') {
        const el = document.getElementById('picker-hours-val');
        let val = parseInt(el.textContent, 10);
        val = dir === 'up' ? val + 1 : val - 1;
        if (val > 12) val = 1;
        if (val < 1) val = 12;
        el.textContent = String(val).padStart(2, '0');
    } else if (col === 'minutes') {
        const el = document.getElementById('picker-minutes-val');
        let val = parseInt(el.textContent, 10);
        val = dir === 'up' ? val + 5 : val - 5;
        if (val >= 60) val = 0;
        if (val < 0) val = 55;
        el.textContent = String(val).padStart(2, '0');
    } else if (col === 'ampm') {
        const el = document.getElementById('picker-ampm-val');
        el.textContent = el.textContent === 'AM' ? 'PM' : 'AM';
    }
}

// ============================================
// Save Handler — sends to backend
// ============================================
function handleSave() {
    const hh = document.getElementById('picker-hours-val').textContent;
    const mm = document.getElementById('picker-minutes-val').textContent;
    const ampm = document.getElementById('picker-ampm-val').textContent;
    const timeStr = `${hh}:${mm} ${ampm}`;

    // Collect selected days
    const selectedDays = [];
    document.querySelectorAll('.day-btn.selected').forEach(b => {
        selectedDays.push(b.dataset.day);
    });

    if (editingAlarmId !== null) {
        // --- Update existing alarm via backend ---
        socket.emit('message', {
            type: 'update_alarm',
            data: {
                id: parseInt(editingAlarmId),
                time: timeStr,
                days: selectedDays,
            }
        });
    } else {
        // --- Create new alarm via backend ---
        socket.emit('message', {
            type: 'create_alarm',
            data: {
                time: timeStr,
                days: selectedDays,
            }
        });
    }

    closeModal();
}