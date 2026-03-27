/**
 * Right panel — Working Memory and User Profile live inspector.
 */

function renderWorkingMemory(wm) {
    const el = document.getElementById('workingMemoryContent');
    if (!wm.active_goal) {
        el.innerHTML = '<div style="color:var(--text-tertiary);font-size:11px">No active goal</div>';
        return;
    }
    const progress = wm.goal_progress;
    const pct = progress.target_amount > 0 ? Math.min(100, (progress.current_amount / progress.target_amount * 100)) : 0;
    el.innerHTML = `
        <div class="memory-kv"><span class="k">Active Goal</span><span class="v" style="font-size:10px">${wm.active_goal}</span></div>
        <div class="progress-bar-wrap">
            <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
            <div class="progress-label"><span>&yen;${progress.current_amount.toLocaleString()}</span><span>&yen;${progress.target_amount.toLocaleString()}</span></div>
        </div>
        <div class="memory-kv"><span class="k">Progress</span><span class="v">${pct.toFixed(1)}%</span></div>
        <div class="memory-kv"><span class="k">Days</span><span class="v">${progress.days_elapsed} / ${progress.days_total}</span></div>
        <div class="memory-kv"><span class="k">Pending</span><span class="v">${wm.pending_suggestions.length} suggestions</span></div>
        <div class="memory-kv"><span class="k">Approved</span><span class="v">${wm.approved_actions.length} actions</span></div>
        ${wm.recent_events.length > 0 ? `
            <div style="margin-top:8px;font-size:10px;color:var(--text-tertiary);text-transform:uppercase;letter-spacing:0.5px">Recent Events</div>
            ${wm.recent_events.slice(-5).reverse().map(e => `
                <div class="mini-event"><span class="mini-icon">${EVENT_CONFIG[e.event_type]?.icon || '📌'}</span>${e.description || e.event_type}</div>
            `).join('')}
        ` : ''}
    `;
    el.classList.add('memory-flash');
    setTimeout(() => el.classList.remove('memory-flash'), 500);
}

function renderUserProfilePanel(profile) {
    const el = document.getElementById('userProfileContent');
    const maxSpend = Math.max(...Object.values(profile.spending_patterns).map(v => v.monthly_avg));
    el.innerHTML = `
        <div class="memory-kv"><span class="k">Income</span><span class="v">&yen;${profile.monthly_income.toLocaleString()}/mo</span></div>
        <div class="memory-kv"><span class="k">Income Cycle</span><span class="v">${profile.income_cycle}</span></div>
        <div class="memory-kv"><span class="k">Risk</span><span class="v">${profile.risk_preference}</span></div>
        <div class="memory-kv"><span class="k">Discretionary</span><span class="v">${(profile.discretionary_ratio * 100).toFixed(0)}%</span></div>
        <div style="margin-top:8px">
            ${Object.entries(profile.spending_patterns).map(([name, data]) => `
                <div class="spending-row">
                    <span class="cat-name">${name}</span>
                    <div class="bar-track"><div class="bar-fill" style="width:${(data.monthly_avg / maxSpend * 100)}%;background:${data.trend === 'increasing' ? 'var(--danger)' : 'var(--primary)'}"></div></div>
                    <span class="bar-value">&yen;${data.monthly_avg}</span>
                </div>
            `).join('')}
        </div>
    `;
}
