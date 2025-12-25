const API_URL = "http://localhost:5000";

const dom = {
    input: document.getElementById('transcriptInput'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    resetBtn: document.getElementById('resetBtn'),
    status: document.getElementById('backendStatus'),
    history: document.getElementById('transcriptHistory'),
    actionsList: document.getElementById('actionItemsList'),
    notesList: document.getElementById('notesList')
};

// Initial State Check
async function checkBackend() {
    try {
        const res = await fetch(`${API_URL}/status`);
        if (res.ok) {
            dom.status.textContent = "Online";
            dom.status.className = "status-badge";
            const data = await res.json();
            renderAll(data);
        } else {
            throw new Error("Backend Error");
        }
    } catch {
        dom.status.textContent = "Offline";
        dom.status.className = "status-badge offline";
    }
}

// Render Functions
function renderAll(data) {
    // History
    dom.history.innerHTML = '';
    data.transcript.slice().reverse().forEach(text => {
        const div = document.createElement('div');
        div.className = 'log-item';
        div.textContent = text;
        dom.history.appendChild(div);
    });

    // Actions
    dom.actionsList.innerHTML = '';
    if (data.action_items.length === 0) {
        dom.actionsList.innerHTML = '<div class="empty-state">No action items detected yet.</div>';
        document.getElementById('saveBtn').style.display = 'none'; // Hide save button
    } else {
        document.getElementById('saveBtn').style.display = 'inline-block'; // Show save button
        data.action_items.slice().forEach((item, index) => {
            const card = document.createElement('div');
            card.className = `card action-item ${item.done ? 'done' : ''}`;
            card.innerHTML = `
                <div class="action-content">
                    <div class="action-meta">
                        <span class="meta-owner">👤 ${item.owner || "Unassigned"}</span>
                        <span>|</span>
                        <span class="meta-date">📅 ${item.deadline || "No Date"}</span>
                    </div>
                    <div class="task-text">${item.task}</div>
                </div>
                <button class="check-btn" onclick="toggleTask(${index})">✓</button>
            `;
            // Insert at top to match "reversed" logic usually desired, or append for chronological
            // Let's prepend to show newest at top like notes usually
            dom.actionsList.prepend(card);
        });
    }

    // Notes
    dom.notesList.innerHTML = '';
    if (data.important_notes.length === 0) {
        dom.notesList.innerHTML = '<div class="empty-state">No notes recorded.</div>';
    } else {
        data.important_notes.forEach(note => {
            const card = document.createElement('div');
            card.className = 'card note-item';
            card.innerHTML = `<div class="note-text">${note}</div>`;
            dom.notesList.prepend(card);
        });
    }
}

// Actions
async function analyzeText() {
    const text = dom.input.value.trim();
    if (!text) return;

    // UI Loading State
    dom.analyzeBtn.classList.add('loading');
    dom.analyzeBtn.disabled = true;

    try {
        const res = await fetch(`${API_URL}/process_text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (res.ok) {
            dom.input.value = ''; // Clear input
            await checkBackend(); // Refresh data
        } else {
            alert("Error processing text");
        }
    } catch (e) {
        alert("Could not connect to backend");
    } finally {
        dom.analyzeBtn.classList.remove('loading');
        dom.analyzeBtn.disabled = false;
    }
}

async function toggleTask(index) {
    // Note: The index passed here relies on the order in the backend array.
    // If we reverse render, we need to map back to original index or just trust backend order.
    // My render loop was `slice().forEach`, so index 0 is backend index 0. 
    // BUT I prepended UI cards. So the visual order is reversed, but the index passed to onclick 
    // inside the loop is the correct backend index.

    try {
        await fetch(`${API_URL}/toggle_task`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ index })
        });
        checkBackend();
    } catch {
        alert("Connection Failed");
    }
}

async function resetSession() {
    // Removed confirmation dialog for instant reset
    await fetch(`${API_URL}/reset`, { method: 'POST' });
    checkBackend();
}

async function saveSession() {
    const title = prompt("Enter a title for this session:");
    if (!title || !title.trim()) return;

    try {
        const res = await fetch(`${API_URL}/save_session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title.trim() })
        });

        if (res.ok) {
            alert(`Session "${title}" saved successfully!`);
            loadSessionsList();
        } else {
            alert("Error saving session");
        }
    } catch {
        alert("Could not connect to backend");
    }
}

async function loadSessionsList() {
    try {
        const res = await fetch(`${API_URL}/list_sessions`);
        const data = await res.json();

        const select = document.getElementById('loadSessionSelect');
        select.innerHTML = '<option value="">Load Session...</option>';

        data.sessions.forEach(session => {
            const option = document.createElement('option');
            option.value = session.filename;
            option.textContent = `${session.title} (${session.item_count} items)`;
            select.appendChild(option);
        });
    } catch {
        console.error("Failed to load sessions list");
    }
}

async function loadSession(filename) {
    if (!filename) return;

    try {
        const res = await fetch(`${API_URL}/load_session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        });

        if (res.ok) {
            const data = await res.json();
            alert(`Session "${data.title}" loaded!`);
            checkBackend();
        } else {
            alert("Error loading session");
        }
    } catch {
        alert("Could not connect to backend");
    }
}

// Event Listeners
dom.analyzeBtn.addEventListener('click', analyzeText);
dom.resetBtn.addEventListener('click', resetSession);
document.getElementById('saveBtn').addEventListener('click', saveSession);
document.getElementById('loadSessionSelect').addEventListener('change', (e) => {
    loadSession(e.target.value);
    e.target.value = ''; // Reset dropdown
});

// Polling / Init
checkBackend();
loadSessionsList(); // Load available sessions on startup
// setInterval(checkBackend, 5000); // Disabled auto-polling - page will only update when you click Analyze or Reset
