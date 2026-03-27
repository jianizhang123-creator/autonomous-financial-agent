/**
 * Main application entry — global state, event configuration, status
 * management, and initialisation.
 */

// Global state
const state = {
    plan: null,
    events: [],
    memory: null,
    running: false,
    eventCounter: 0,
    currentEventType: null
};

// Event type configuration
const EVENT_CONFIG = {
    income_received: {
        icon: '💰', label: 'Income Received', cssClass: 'income',
        fields: [
            {id: 'amount', label: 'Amount (¥)', type: 'number', default: 8000},
            {id: 'source', label: 'Source', type: 'text', default: '月薪'}
        ]
    },
    large_expense: {
        icon: '💸', label: 'Large Expense', cssClass: 'expense',
        fields: [
            {id: 'amount', label: 'Amount (¥)', type: 'number', default: 1500},
            {id: 'category', label: 'Category', type: 'text', default: '购物'},
            {id: 'merchant', label: 'Merchant', type: 'text', default: '京东'},
            {id: 'description', label: 'Description', type: 'text', default: '买了新耳机'}
        ]
    },
    budget_threshold: {
        icon: '⚠️', label: 'Budget Alert', cssClass: 'budget',
        fields: [
            {id: 'category', label: 'Category', type: 'text', default: '餐饮'},
            {id: 'current_spent', label: 'Current Spent (¥)', type: 'number', default: 1530},
            {id: 'budget_limit', label: 'Budget Limit (¥)', type: 'number', default: 1800},
            {id: 'percentage', label: 'Percentage (%)', type: 'number', default: 85}
        ]
    },
    milestone_reached: {
        icon: '🎯', label: 'Milestone Reached', cssClass: 'milestone',
        fields: [
            {id: 'milestone_type', label: 'Type', type: 'text', default: '阶段储蓄目标'},
            {id: 'amount_saved', label: 'Saved (¥)', type: 'number', default: 1000},
            {id: 'target_amount', label: 'Target (¥)', type: 'number', default: 5000}
        ]
    },
    bill_due: {
        icon: '📅', label: 'Bill Due', cssClass: 'bill',
        fields: [
            {id: 'bill_name', label: 'Bill Name', type: 'text', default: '花呗'},
            {id: 'amount', label: 'Amount (¥)', type: 'number', default: 2000},
            {id: 'due_date', label: 'Due Date', type: 'text', default: '2026-04-01'}
        ]
    },
    anomaly_detected: {
        icon: '🔍', label: 'Anomaly Detected', cssClass: 'anomaly',
        fields: [
            {id: 'category', label: 'Category', type: 'text', default: '娱乐'},
            {id: 'usual_amount', label: 'Usual (¥)', type: 'number', default: 600},
            {id: 'actual_amount', label: 'Actual (¥)', type: 'number', default: 1500},
            {id: 'period', label: 'Period', type: 'text', default: '本周'}
        ]
    }
};

// Status bar
function setStatus(status, text) {
    const dot = document.getElementById('statusDot');
    const label = document.getElementById('statusText');
    dot.className = status === 'running' ? 'status-dot' : status === 'error' ? 'status-dot inactive' : 'status-dot';
    if (status === 'running') dot.style.background = 'var(--warning)';
    else if (status === 'error') dot.style.background = 'var(--danger)';
    else dot.style.background = 'var(--success)';
    label.textContent = text;
}

function enableEventButtons() {
    document.querySelectorAll('.event-btn').forEach(b => b.disabled = false);
}

// Load initial status from server
async function loadStatus() {
    try {
        const res = await fetch('/api/status');
        state.memory = await res.json();
        renderProfile(state.memory.user_profile);
        renderWorkingMemory(state.memory.working_memory);
        renderUserProfilePanel(state.memory.user_profile);
        if (state.memory.working_memory.active_goal) {
            enableEventButtons();
        }
    } catch (e) {
        console.error('Failed to load status:', e);
    }
}

// Initialise
document.addEventListener('DOMContentLoaded', async () => {
    await loadPresets();
    await loadStatus();
});
