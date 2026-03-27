/**
 * Left panel — Presets, goal form, profile display, and plan rendering.
 */

async function loadPresets() {
    try {
        const res = await fetch('/api/presets');
        const presets = await res.json();
        const container = document.getElementById('presetsContainer');
        container.innerHTML = presets.map(p => `
            <div class="preset-card" onclick="selectPreset(${JSON.stringify(p).replace(/"/g, '&quot;')})">
                <div class="preset-name">${p.name}</div>
                <div class="preset-name-en">${p.name_en}</div>
                <div class="preset-desc">${p.description}</div>
            </div>
        `).join('');
    } catch (e) {
        console.error('Failed to load presets:', e);
    }
}

function selectPreset(preset) {
    document.getElementById('goalInput').value = preset.goal;
    document.getElementById('goalType').value = preset.goal_type;
    document.getElementById('targetAmount').value = preset.target_amount;
    document.getElementById('targetDays').value = preset.target_days;
    document.querySelectorAll('.preset-card').forEach(c => c.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

function renderProfile(profile) {
    const maxSpend = Math.max(...Object.values(profile.spending_patterns).map(v => v.monthly_avg));
    const el = document.getElementById('profileContent');
    el.innerHTML = `
        <div class="profile-item"><span class="label">Monthly Income</span><span class="value">&yen;${profile.monthly_income.toLocaleString()}</span></div>
        <div class="profile-item"><span class="label">Monthly Expense</span><span class="value">&yen;${profile.total_monthly_expense.toLocaleString()}</span></div>
        <div class="profile-item"><span class="label">Risk Preference</span><span class="badge badge-${profile.risk_preference === 'moderate' ? 'primary' : profile.risk_preference === 'aggressive' ? 'danger' : 'success'}">${profile.risk_preference}</span></div>
        <div class="profile-item"><span class="label">Goals Completed</span><span class="value">${profile.historical_goals.filter(g => g.status === 'completed').length}/${profile.historical_goals.length}</span></div>
        <div class="spending-bar-wrap">
            ${Object.entries(profile.spending_patterns).map(([name, data]) => `
                <div class="spending-row">
                    <span class="cat-name">${name}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:${(data.monthly_avg / maxSpend * 100)}%"></div></div>
                    <span class="bar-value">&yen;${data.monthly_avg}</span>
                </div>
            `).join('')}
        </div>
    `;
}

// --- Plan creation & rendering ---

async function createPlan() {
    const goal = document.getElementById('goalInput').value.trim();
    const goalType = document.getElementById('goalType').value;
    const targetAmount = parseInt(document.getElementById('targetAmount').value) || 0;
    const targetDays = parseInt(document.getElementById('targetDays').value) || 0;
    if (!goal || !targetAmount || !targetDays) return;

    state.running = true;
    setStatus('running', 'Creating plan...');
    document.getElementById('createPlanBtn').disabled = true;
    document.getElementById('welcomeState').style.display = 'none';
    const planEl = document.getElementById('planContent');
    planEl.style.display = 'block';
    planEl.innerHTML = renderAgentPipeline(['goal_decomposition', 'planning'], {});

    const handlers = {
        agent_start: (data) => {
            updatePipelineStep(data.agent, 'running');
            setStatus('running', `Agent: ${data.agent}...`);
        },
        agent_done: (data) => {
            updatePipelineStep(data.agent, 'done');
            if (data.agent === 'goal_decomposition') {
                state.plan = { decomposition: data.result };
            } else if (data.agent === 'planning') {
                state.plan.budget = data.result;
            }
        },
        plan_complete: (data) => {
            state.plan = data;
            renderPlan(data);
            enableEventButtons();
            state.running = false;
            setStatus('ready', 'Plan created');
            document.getElementById('createPlanBtn').disabled = false;
        },
        memory_update: (data) => {
            state.memory = data;
            renderWorkingMemory(data.working_memory);
            renderUserProfilePanel(data.user_profile);
        },
        error: (data) => {
            state.running = false;
            setStatus('error', 'Error occurred');
            document.getElementById('createPlanBtn').disabled = false;
        }
    };

    await streamSSE('/api/plan', {goal, goal_type: goalType, target_amount: targetAmount, target_days: targetDays}, handlers);
}

function renderAgentPipeline(agents, statuses) {
    const labels = {
        goal_decomposition: 'Goal Decomposition',
        planning: 'Planning Agent',
        event_router: 'Event Router',
        execution_monitor: 'Execution Monitor',
        insight: 'Insight Agent'
    };
    return `<div class="agent-pipeline" id="agentPipeline">${agents.map((a, i) => {
        const s = statuses[a] || 'waiting';
        return (i > 0 ? `<div class="agent-connector ${s === 'done' ? 'done' : ''}" id="conn_${a}"></div>` : '') +
            `<div class="agent-step ${s}" id="step_${a}">
                <div class="step-icon">${s === 'done' ? '✓' : s === 'running' ? '⟳' : (i+1)}</div>
                ${labels[a] || a}
            </div>`;
    }).join('')}</div>`;
}

function updatePipelineStep(agent, status) {
    const step = document.getElementById(`step_${agent}`);
    if (!step) return;
    step.className = `agent-step ${status}`;
    const icon = step.querySelector('.step-icon');
    if (icon) icon.textContent = status === 'done' ? '✓' : status === 'running' ? '⟳' : icon.textContent;
    const conn = document.getElementById(`conn_${agent}`);
    if (conn && status === 'done') conn.classList.add('done');
}

function renderPlan(data) {
    const planEl = document.getElementById('planContent');
    const decomp = data.decomposition || {};
    const budget = data.budget || {};
    const phases = decomp.phases || [];

    planEl.innerHTML = renderAgentPipeline(['goal_decomposition', 'planning'], {goal_decomposition: 'done', planning: 'done'}) + `
        <div class="plan-section">
            <div class="card">
                <div class="card-title">📋 Goal Summary</div>
                <div class="goal-summary">
                    <div class="goal-stat"><div class="stat-value">&yen;${(data.target_amount || 0).toLocaleString()}</div><div class="stat-label">Target</div></div>
                    <div class="goal-stat"><div class="stat-value">${data.target_days || 0}</div><div class="stat-label">Days</div></div>
                    <div class="goal-stat"><div class="stat-value">${phases.length}</div><div class="stat-label">Phases</div></div>
                    <div class="goal-stat"><div class="stat-value">${decomp.total_duration_weeks || '-'}</div><div class="stat-label">Weeks</div></div>
                </div>
            </div>
        </div>

        <div class="plan-section">
            <div class="card">
                <div class="card-title">📅 Phase Timeline</div>
                <div class="phase-timeline">
                    ${phases.map(p => `
                        <div class="phase-item">
                            <div class="phase-name">${p.name}</div>
                            <div class="phase-meta">
                                <span>${p.duration_weeks} weeks</span>
                                <span>Save &yen;${p.weekly_savings_target}/week</span>
                                <span>Budget &le; &yen;${p.weekly_budget_limit}/week</span>
                            </div>
                            ${(p.milestones && p.milestones.length) ? `
                                <div class="phase-milestones">
                                    ${p.milestones.map(m => `<div class="milestone-item">Week ${m.week}: ${m.description} (&yen;${m.target_amount})</div>`).join('')}
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        ${budget.budget_plan ? `
        <div class="plan-section">
            <div class="card">
                <div class="card-title">💰 Budget Adjustments</div>
                <table class="budget-table">
                    <thead><tr><th>Category</th><th>Current</th><th>Recommended</th><th>Change</th><th>Strategy</th></tr></thead>
                    <tbody>
                        ${(budget.budget_plan.categories || []).map(c => {
                            const diff = c.recommended - c.current_avg;
                            const cls = diff < 0 ? 'decrease' : diff > 0 ? 'increase' : 'same';
                            const sign = diff < 0 ? '' : '+';
                            return `<tr>
                                <td><strong>${c.name}</strong></td>
                                <td>&yen;${c.current_avg}</td>
                                <td>&yen;${c.recommended}</td>
                                <td><span class="budget-change ${cls}">${sign}${diff} (${c.reduction_pct}%)</span></td>
                                <td style="font-size:11px;color:var(--text-secondary)">${c.strategy || ''}</td>
                            </tr>`;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
        ` : ''}

        ${budget.tips ? `
        <div class="plan-section">
            <div class="card">
                <div class="card-title">💡 Tips</div>
                <ul class="tips-list">
                    ${budget.tips.map(t => `<li>${t}</li>`).join('')}
                </ul>
            </div>
        </div>
        ` : ''}
    `;
}
