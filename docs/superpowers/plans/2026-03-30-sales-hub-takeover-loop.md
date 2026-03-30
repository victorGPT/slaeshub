# Sales Hub Takeover Loop Plan

> For agentic workers: REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish a durable execution loop for the prototype repo, then unify mock data so all prototype pages can advance from one shared source of truth.

**Architecture:** Add a repo-local coordination layer with one active domain (`prototype`) and four serial tasks. Keep the prototype file-based: Python scripts generate client data and page artifacts, while runtime HTML pages read a generated shared data file for entity-specific views.

**Tech Stack:** Python 3 standard library, static HTML, Tailwind CDN, vanilla JavaScript, YAML coordination records.

---

## Task Packets

### Task 1: Unify mock data contract

**Intent**

- Introduce one shared runtime data contract for clients, rankings, and events.
- Keep homepage and client list generation script-driven.
- Generate a browser-loadable `prototype/mock-data.js` file from Python.

**Files**

- Modify: `scripts/generate_prototype.py`
- Modify: `scripts/simulate_clients.py` if data contract helpers are needed
- Create: `prototype/mock-data.js`
- Regenerate: `prototype/home-a.html`, `prototype/home-b.html`, `prototype/home-c.html`, `prototype/clients.html`

**Constraints**

- Must keep local `file://` opening working.
- Must not introduce build tooling or fetch-based runtime loading.

**Verification**

- `python3 scripts/simulate_clients.py`
- `python3 scripts/generate_prototype.py`
- `open prototype/index.html`

**Definition of Done**

- Shared data file is generated.
- Generated pages use stable query params for client navigation.
- No page invents a separate client id scheme.

### Task 2: Connect client detail to shared mock data

**Intent**

- Replace the hardcoded `王伟明` detail page with uid-driven rendering from shared data.

**Files**

- Modify: `prototype/client-detail.html`
- Consume: `prototype/mock-data.js`

**Constraints**

- Keep the existing dark-style layout and inline interaction style.
- Related event links must carry event ids.

**Verification**

- `open 'prototype/client-detail.html?uid=<known-uid>'`
- Compare the same uid against homepage/client list values.

**Definition of Done**

- Multiple uid values render different clients.
- Header, tags, metrics, business lines, notes, records, and related events come from shared data.

### Task 3: Connect events and event thread to shared mock data

**Intent**

- Render the event list and event thread from the same event dataset.

**Files**

- Modify: `prototype/events.html`
- Modify: `prototype/event-thread.html`
- Consume: `prototype/mock-data.js`

**Constraints**

- Preserve the four-state interaction in the thread page.
- Event thread must be resolvable by `event` query param.

**Verification**

- `open prototype/events.html`
- `open 'prototype/event-thread.html?event=<known-event-id>'`

**Definition of Done**

- Event cards and thread detail match for the same event.
- Thread page resolves the correct client and suggestion content.

### Task 4: Consolidate v1 legacy entry points

**Intent**

- Keep v1 assets, but ensure no current-state instruction points to them as active entry points.

**Files**

- Modify: `README.md`
- Modify: `docs/prototype-prompt-v2.md`
- Modify: `docs/prototype-prompt.md` if explicit legacy banner is needed
- Optionally annotate: `prototype/home.html`

**Constraints**

- Do not delete historical files in this round.

**Verification**

- `rg -n "home\\.html" README.md docs/prototype-prompt*.md prototype/index.html`

**Definition of Done**

- Active flow is documented as `home-a.html`, `home-b.html`, `home-c.html`.
- Any remaining `home.html` references are clearly marked legacy.
