# Autonomous Financial Agent

> "Save 5000 in 3 months." That's the entire instruction. The agent handles everything else.

A goal-driven autonomous agent system that decomposes financial goals into executable plans, monitors progress through real-time event streams, and autonomously proposes adjustments — with human-in-the-loop approval at every decision point.

## Product Insight

### From Command-Driven to Goal-Driven

Most financial AI products are **command-driven**: the user says "record this expense," and the AI obeys. This creates a ceiling — the user must know what to do and when to do it. The value prop is speed, not intelligence.

This project explores the next paradigm: **goal-driven autonomy.** The user delegates a financial objective, and the agent takes ownership of the entire execution lifecycle:

```
Command-Driven:  User → tells agent what to do → Agent executes
Goal-Driven:     User → tells agent what to achieve → Agent plans, monitors, adjusts
```

| Aspect | Command-Driven | Goal-Driven (This Project) |
|--------|---------------|---------------------------|
| User role | Operator (issues commands) | Delegator (sets objectives) |
| Agent role | Executor | Planner + Monitor + Advisor |
| Decision making | User decides everything | Agent proposes, user approves |
| Adaptability | None (static responses) | Dynamic (replans on deviation) |
| Memory | Stateless or shallow | Dual-layer cognitive architecture |

### Why Human-in-the-Loop Matters

The agent is autonomous but **not unsupervised.** Every actionable suggestion requires explicit user approval. This isn't a limitation — it's a design principle:

1. **Financial decisions have real consequences** — unlike content generation, bad financial advice costs money
2. **Trust is built incrementally** — users need to see the agent make good suggestions before they delegate more
3. **Approval data feeds the memory system** — every approve/reject teaches the agent about user preferences

The interaction model is: **Agent autonomy + Human oversight = Calibrated trust.**

## Architecture

### 5-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     Goal Delegation                          │
│  "三个月攒5000块" / "Pay off ¥8000 debt" / "Cut delivery 30%"│
└─────────────────────────┬───────────────────────────────────┘
                          │
              ┌───────────▼──────────────┐
              │  Goal Decomposition Agent │  Breaks goal into
              │  目标拆解                 │  phased sub-tasks with
              │                          │  weekly budget constraints
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │  Planning Agent           │  Generates execution plan
              │  规划引擎                 │  with category-level budget
              │                          │  adjustments + savings schedule
              └───────────┬──────────────┘
                          │
                          ▼
              ┌──── Active Plan ──────┐
              │  Milestones, budgets, │ ◄──── Stored in Working Memory
              │  weekly targets       │
              └───────────────────────┘
                          │
            ══════════════╪══════════════  Financial Events Stream
            💰 Income  💸 Expense  ⚠️ Budget  🎯 Milestone  📅 Bill  🔍 Anomaly
                          │
              ┌───────────▼──────────────┐
              │  Event Router             │  Classifies priority
              │  事件路由                 │  (critical/high/medium/low)
              │                          │  and routes to handler
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │  Execution Monitor        │  Detects plan deviation
              │  执行监控                 │  and generates adjustment
              │                          │  suggestions
              └───────────┬──────────────┘
                          │
              ┌───────────▼──────────────┐
              │  Insight Agent            │  Generates explainable
              │  可解释决策               │  rationale for every
              │                          │  suggestion
              └───────────┬──────────────┘
                          │
                          ▼
              ┌──── Suggestion Card ──────┐
              │  Action + Rationale +     │
              │  Expected Impact          │
              │  [✓ Approve] [✗ Reject]   │ ◄──── Human-in-the-Loop
              └───────────────────────────┘
                          │
                          ▼
              ┌──── Memory Update ────────┐
              │  Working Memory refreshed │
              │  User Profile evolved     │
              └───────────────────────────┘
```

### Dual-Layer Memory System

```
┌─────────────────────────────────────────────────┐
│              Working Memory (Session)             │
│                                                   │
│  • Active goal + current plan                    │
│  • Recent event queue (last 10)                  │
│  • Pending suggestions awaiting approval         │
│  • Approved actions history                      │
│  • Goal progress (amount saved, days elapsed)    │
│                                                   │
│  Lifecycle: Created on goal setup, evolves       │
│  through events, resets on new goal              │
├─────────────────────────────────────────────────┤
│              User Profile (Persistent)            │
│                                                   │
│  • Income structure (amount, cycle)              │
│  • Spending patterns by category (avg + trend)   │
│  • Risk preference (conservative/moderate/aggressive) │
│  • Historical goal completion rate               │
│  • Intervention response patterns                │
│                                                   │
│  Lifecycle: Persists across goals, evolves       │
│  through approved/rejected suggestions           │
└─────────────────────────────────────────────────┘
```

**Why two layers?** Working Memory gives the agent session context ("what am I doing right now?"). User Profile gives the agent behavioral understanding ("what kind of person is this?"). Together, they enable the agent to make contextually aware suggestions that match both the current situation and the user's long-term patterns.

### Event-Driven Decision Architecture

The system processes 6 event types with priority-based routing:

| Event | Priority | Trigger | Agent Response |
|-------|----------|---------|---------------|
| `budget_threshold` | Critical/High | 80% or 100% budget consumed | Immediate spending adjustment |
| `large_expense` | High | Above-threshold purchase | Impact analysis + replan |
| `bill_due` | High | Recurring bill approaching | Cash flow warning |
| `anomaly_detected` | Medium | Unusual spending pattern | Investigation + suggestion |
| `income_received` | Low | Salary/bonus arrives | Progress update + allocation advice |
| `milestone_reached` | Low | Savings checkpoint hit | Celebration + next phase preview |

Every event triggers a 3-agent chain: **Router → Monitor → Insight**, producing an explainable suggestion with approve/reject controls.

## Interactive Demo

### Three-Panel Layout

- **Left**: Goal setup form, 3 preset scenarios, live user profile summary
- **Center**: Plan timeline visualization, real-time event feed with agent decision chains
- **Right**: Live memory inspector (working memory + user profile), updates on every action

### Bottom Event Simulator

6 event type buttons + "Simulate Day" for quick testing. Each button opens a modal with pre-filled, editable event parameters. "Simulate Day" generates a random event with realistic values.

### Demo Flow

1. Pick a preset (e.g., "三个月攒5000块")
2. Watch Goal Decomposition + Planning agents create a phased plan (streamed via SSE)
3. Trigger events from the bottom bar
4. See the 3-agent decision chain process each event in real-time
5. Approve or reject suggestions — watch memory panels update live
6. Track progress toward the goal

## Demo Presets

| Preset | Type | Target | Duration | Difficulty |
|--------|------|--------|----------|------------|
| **三个月攒5000块** | Savings | ¥5,000 | 90 days | Moderate |
| **还清信用卡8000元** | Debt Repayment | ¥8,000 | 60 days | Aggressive |
| **每月减少外卖开支30%** | Spending Reduction | ¥270/mo | 30 days | Behavioral |

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| **AI** | Claude API (Haiku 4.5) | Optimized for speed in multi-agent chains; 5 agents need fast inference |
| **Backend** | Flask + SSE | Lightweight streaming without WebSocket complexity |
| **Frontend** | Vanilla HTML/CSS/JS | Zero build step, modular components, portfolio-friendly |
| **Memory** | JSON file | Dual-layer state management without database overhead |
| **Testing** | pytest | Unit + integration tests for agents, memory, and routes |

## Project Structure

```
autonomous-financial-agent/
├── app.py                         # Flask entry point — registers blueprints, serves frontend
├── config.py                      # Shared constants (model, paths)
│
├── agents/                        # 5 specialized agents, each independently iterable
│   ├── base.py                    # Claude API calls, JSON parsing, prompt loading
│   ├── goal_decomposition.py      # Breaks goals into phased sub-tasks
│   ├── planning.py                # Category-level budget adjustments
│   ├── event_router.py            # Priority classification + routing
│   ├── execution_monitor.py       # Plan deviation detection + adjustment
│   └── insight.py                 # Empathetic explanation generation
│
├── prompts/                       # System prompts as standalone markdown (decoupled from code)
│   ├── goal_decomposition.md
│   ├── planning.md
│   ├── event_router.md
│   ├── execution_monitor.md
│   └── insight.md
│
├── memory/                        # Dual-layer memory system
│   ├── store.py                   # JSON persistence (load / save)
│   ├── user_profile.py            # Profile → markdown context formatter
│   └── working_memory.py          # Session state → markdown context formatter
│
├── events/
│   └── stream.py                  # Server-Sent Events formatting
│
├── routes/                        # Flask Blueprints — one per pipeline
│   ├── plan.py                    # POST /api/plan (Goal Decomposition → Planning)
│   ├── event.py                   # POST /api/event (Router → Monitor → Insight)
│   └── approve.py                 # POST /api/approve + GET /api/status, /api/presets
│
├── presets/
│   └── scenarios.py               # 3 demo financial goals
│
├── static/                        # Frontend assets
│   ├── index.html                 # HTML skeleton
│   ├── css/style.css              # All styles
│   └── js/
│       ├── api.js                 # SSE streaming client
│       ├── app.js                 # State management + initialization
│       └── components/
│           ├── goal-panel.js      # Left panel: presets, goal form, plan rendering
│           ├── event-feed.js      # Center: event cards, agent chain, suggestions
│           └── memory-inspector.js# Right panel: live memory display
│
├── tests/                         # pytest test suite
│   ├── test_agents.py             # JSON parsing, prompt loading
│   ├── test_memory.py             # Memory CRUD, context formatters
│   └── test_routes.py             # API endpoint integration tests
│
└── data/
    └── memory.json                # Runtime persistent state (gitignored)
```

## Quick Start

```bash
git clone https://github.com/jianizhang123-creator/autonomous-financial-agent.git
cd autonomous-financial-agent

pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here

python app.py                      # → http://localhost:8080

# Run tests
pytest tests/ -v
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Goal-driven, not command-driven | Users delegate outcomes, not procedures — this is the agent paradigm shift |
| Human-in-the-loop for all actions | Financial decisions are irreversible; trust must be earned through good suggestions |
| Dual-layer memory | Working Memory for "what's happening now" + User Profile for "who is this person" — both needed for contextual decisions |
| Event-driven, not polling | Real-time event streams enable autonomous detection + response, not just periodic check-ins |
| Explainable rationale on every suggestion | Black-box financial advice is unacceptable; every recommendation shows its reasoning |
| Priority-based event routing | Not all events deserve the same urgency — budget breaches are critical, income arrivals are informational |
| 3-agent event chain | Separation of concerns: Router classifies, Monitor analyzes, Insight explains — each independently testable |

---

*Built to validate that autonomous agents can handle goal-directed financial planning with appropriate human oversight — demonstrating that the future of AI products is not "AI does everything" but "AI proposes, human decides, system learns."*
