/**
 * Center panel — Event simulation, modal, trigger pipeline, and
 * suggestion approve / reject interactions.
 */

function showEventModal(eventType) {
    if (state.running) return;
    state.currentEventType = eventType;
    const config = EVENT_CONFIG[eventType];
    document.getElementById('modalTitle').textContent = `${config.icon} ${config.label}`;
    document.getElementById('modalFields').innerHTML = config.fields.map(f => `
        <div class="form-group">
            <label class="form-label">${f.label}</label>
            <input type="${f.type}" class="form-input" id="modal_${f.id}" value="${f.default}">
        </div>
    `).join('');
    document.getElementById('modalOverlay').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').classList.remove('active');
    state.currentEventType = null;
}

async function submitEvent() {
    const config = EVENT_CONFIG[state.currentEventType];
    const eventData = {};
    config.fields.forEach(f => {
        const val = document.getElementById(`modal_${f.id}`).value;
        eventData[f.id] = f.type === 'number' ? parseFloat(val) : val;
    });
    closeModal();
    await triggerEvent(state.currentEventType, eventData);
}

async function simulateDay() {
    if (state.running) return;
    const types = Object.keys(EVENT_CONFIG);
    const type = types[Math.floor(Math.random() * types.length)];
    const config = EVENT_CONFIG[type];
    const eventData = {};
    config.fields.forEach(f => {
        if (f.type === 'number') {
            const base = f.default;
            eventData[f.id] = Math.round(base * (0.7 + Math.random() * 0.6));
        } else {
            eventData[f.id] = f.default;
        }
    });
    await triggerEvent(type, eventData);
}

async function triggerEvent(eventType, eventData) {
    state.running = true;
    state.eventCounter++;
    const eventId = `evt_${state.eventCounter}`;
    setStatus('running', `Processing ${eventType}...`);
    document.querySelectorAll('.event-btn').forEach(b => b.disabled = true);

    const config = EVENT_CONFIG[eventType];
    const feedEl = document.getElementById('eventFeed');

    // Create event card
    const cardHtml = `
        <div class="event-card" id="${eventId}">
            <div class="event-header">
                <div class="event-type-icon ${config.cssClass}">${config.icon}</div>
                <div class="event-info">
                    <div class="event-title">${config.label}</div>
                    <div class="event-desc">${formatEventDesc(eventType, eventData)}</div>
                </div>
                <span class="event-priority" id="${eventId}_priority">Processing...</span>
                <span class="event-timestamp">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="agent-chain" id="${eventId}_chain">
                <span class="chain-step" id="${eventId}_chain_event_router">Event Router</span>
                <span class="chain-arrow">&rarr;</span>
                <span class="chain-step" id="${eventId}_chain_execution_monitor">Monitor</span>
                <span class="chain-arrow">&rarr;</span>
                <span class="chain-step" id="${eventId}_chain_insight">Insight</span>
            </div>
            <div id="${eventId}_suggestion"></div>
        </div>
    `;
    feedEl.insertAdjacentHTML('afterbegin', cardHtml);

    const handlers = {
        event_received: () => {},
        agent_start: (data) => {
            const chainStep = document.getElementById(`${eventId}_chain_${data.agent}`);
            if (chainStep) chainStep.classList.add('running');
        },
        agent_done: (data) => {
            const chainStep = document.getElementById(`${eventId}_chain_${data.agent}`);
            if (chainStep) {
                chainStep.classList.remove('running');
                chainStep.classList.add('done');
            }
            if (data.agent === 'event_router' && data.result) {
                const prEl = document.getElementById(`${eventId}_priority`);
                if (prEl) {
                    const p = (data.result.priority || 'medium').toLowerCase();
                    prEl.className = `event-priority priority-${p}`;
                    prEl.textContent = p.charAt(0).toUpperCase() + p.slice(1);
                }
            }
        },
        event_complete: (data) => {
            renderSuggestion(eventId, data);
            state.running = false;
            setStatus('ready', 'Event processed');
            enableEventButtons();
        },
        memory_update: (data) => {
            state.memory = data;
            renderWorkingMemory(data.working_memory);
            renderUserProfilePanel(data.user_profile);
        },
        error: () => {
            state.running = false;
            setStatus('error', 'Error');
            enableEventButtons();
        }
    };

    await streamSSE('/api/event', {event_type: eventType, event_data: eventData}, handlers);
}

function formatEventDesc(type, data) {
    switch (type) {
        case 'income_received': return `&yen;${data.amount} from ${data.source}`;
        case 'large_expense': return `&yen;${data.amount} at ${data.merchant} (${data.category})`;
        case 'budget_threshold': return `${data.category} at ${data.percentage}% of budget`;
        case 'milestone_reached': return `Saved &yen;${data.amount_saved} of &yen;${data.target_amount}`;
        case 'bill_due': return `${data.bill_name} &yen;${data.amount} due ${data.due_date}`;
        case 'anomaly_detected': return `${data.category}: &yen;${data.actual_amount} vs usual &yen;${data.usual_amount}`;
        default: return JSON.stringify(data);
    }
}

function renderSuggestion(eventId, data) {
    const el = document.getElementById(`${eventId}_suggestion`);
    if (!el) return;
    const s = data.suggestion || {};
    const insight = data.insight || {};
    const monitor = data.monitor || {};
    const suggestionId = data.suggestion_id || `sug_${state.eventCounter}`;

    el.innerHTML = `
        <div class="suggestion-card">
            <div class="suggestion-headline">${insight.headline || s.action || 'Agent Suggestion'}</div>
            <div class="suggestion-body">${insight.explanation || s.description || monitor.suggestion?.description || ''}</div>
            ${s.expected_impact || monitor.suggestion?.expected_impact ? `
                <div class="suggestion-impact"><strong>Expected Impact:</strong> ${s.expected_impact || monitor.suggestion?.expected_impact || ''}</div>
            ` : ''}
            <div class="suggestion-rationale">
                <strong>Rationale:</strong> ${monitor.rationale || insight.risk_note || s.rationale || 'Based on current plan analysis'}
                ${insight.supporting_factors ? `<br><strong>Supporting factors:</strong> ${insight.supporting_factors.join('; ')}` : ''}
            </div>
            <div class="suggestion-actions" id="${suggestionId}_actions">
                <button class="btn-approve" onclick="approveSuggestion('${suggestionId}', true)">✓ Approve</button>
                <button class="btn-reject" onclick="approveSuggestion('${suggestionId}', false)">✗ Reject</button>
            </div>
        </div>
    `;
}

async function approveSuggestion(suggestionId, approved) {
    const actionsEl = document.getElementById(`${suggestionId}_actions`);
    if (!actionsEl) return;
    actionsEl.innerHTML = `<div class="suggestion-resolved ${approved ? 'approved' : 'rejected'}">${approved ? '✓ Approved — plan updated' : '✗ Rejected — no changes made'}</div>`;

    try {
        const res = await fetch('/api/approve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({suggestion_id: suggestionId, approved})
        });
        const data = await res.json();
        if (data.memory) {
            state.memory = data.memory;
            renderWorkingMemory(data.memory.working_memory);
            renderUserProfilePanel(data.memory.user_profile);
        }
    } catch (e) {
        console.error('Approve failed:', e);
    }
}
