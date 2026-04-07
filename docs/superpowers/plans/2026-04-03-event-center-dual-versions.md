# Event Center Dual Versions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the prototype event center into an embedded-tab version and a standalone-star version with shared localStorage state for flagged and closed events.

**Architecture:** Introduce one shared browser/Node-compatible helper module under `prototype/` that owns event normalization, flagged/closed state handling, deadline badge mapping, and filtering. Keep each HTML page self-contained at the layout layer while delegating shared behavior to that module, and update the detail page close action to write the same close-state key.

**Tech Stack:** Static HTML, Tailwind CDN, vanilla JavaScript, localStorage, Python `pytest`, Node.js

---

## Task 1: Lock Shared Event Logic With Tests

**Files:**
- Create: `tests/test_event_center_shared.py`
- Create: `prototype/event-center-shared.js`

- [ ] **Step 1: Write the failing test**

```python
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "prototype" / "event-center-shared.js"


def run_node(script: str):
    return subprocess.run(
        ["node", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_compute_flagged_view_orders_by_flagged_time_and_marks_closed():
    script = f"""
    const shared = require({json.dumps(str(MODULE))});
    const events = [
      {{ id: 'fu_1', title: 'A', type: '主动联系', client_name: '甲', created_at: '2026-04-01T10:00:00Z', status: '跟进中' }},
      {{ id: 'fu_2', title: 'B', type: '客户反馈', client_name: '乙', created_at: '2026-04-02T10:00:00Z', status: '跟进中' }}
    ];
    const flagged = [
      {{ fuId: 'fu_1', deadline: 'month', flaggedAt: '2026-04-02T08:00:00Z' }},
      {{ fuId: 'fu_2', deadline: 'today', flaggedAt: '2026-04-03T08:00:00Z' }}
    ];
    const result = shared.computeFlaggedView(events, flagged, ['fu_1']);
    console.log(JSON.stringify(result));
    """
    result = run_node(script)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [row["id"] for row in payload["items"]] == ["fu_2", "fu_1"]
    assert payload["items"][0]["deadlineLabel"] == "本日"
    assert payload["items"][1]["isClosed"] is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: FAIL because `prototype/event-center-shared.js` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```javascript
function computeFlaggedView(events, flaggedEntries, closedIds) {
  const closedSet = new Set(closedIds || []);
  const eventMap = new Map((events || []).map((event) => [String(event.id || ""), event]));
  const deadlineMeta = {
    today: { label: "本日", color: "#F6465D" },
    week: { label: "本周", color: "#F0B90B" },
    month: { label: "本月", color: "#848E9C" },
  };

  return {
    items: (flaggedEntries || [])
      .slice()
      .sort((a, b) => new Date(b.flaggedAt || 0).getTime() - new Date(a.flaggedAt || 0).getTime())
      .map((entry) => {
        const event = eventMap.get(String(entry.fuId || "")) || {};
        const meta = deadlineMeta[entry.deadline] || deadlineMeta.month;
        return {
          id: String(event.id || entry.fuId || ""),
          title: String(event.title || "—"),
          deadlineLabel: meta.label,
          deadlineColor: meta.color,
          isClosed: closedSet.has(String(event.id || entry.fuId || "")),
        };
      }),
  };
}

module.exports = { computeFlaggedView };
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: PASS


## Task 2: Build Shared Event Center Runtime

**Files:**
- Modify: `prototype/event-center-shared.js`
- Modify: `prototype/events.html`
- Create: `prototype/events-b.html`
- Create: `prototype/star.html`

- [ ] **Step 1: Extend tests with all required behaviors**

Add assertions for:
- flagged count badge hidden at `0`
- all-events filter pills keep closed rows in list
- deadline choice writes `{ fuId, deadline, flaggedAt }`
- closed rows render with reduced opacity markers in derived view

- [ ] **Step 2: Run tests to verify new assertions fail**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: FAIL on missing helpers for counts, filters, or deadline state.

- [ ] **Step 3: Implement shared helpers and page bootstrap**

Implement:
- storage readers/writers for `slaesh_flagged` and `slaesh_closed`
- event normalization from `follow_up_events`
- derived views for Version A all/flagged tabs
- derived views for Version B all-events page and `star.html`
- HTML renderers for cards, star chooser strip, filter pills, and empty states

- [ ] **Step 4: Run tests to verify it passes**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: PASS


## Task 3: Wire Detail-Page Close Action

**Files:**
- Modify: `prototype/follow-up-thread.html`

- [ ] **Step 1: Write the failing test**

Add a Node-backed assertion that closing an event appends its `fuId` to `slaesh_closed` without duplicating entries.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: FAIL because close-state mutation helper is missing.

- [ ] **Step 3: Implement the close-state mutation helper and call it from detail page**

Update the shared module with a `closeEvent` helper and update the detail page bottom action button to invoke it before reloading/back-navigation.

- [ ] **Step 4: Run tests to verify it passes**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: PASS


## Task 4: Verify Browser Behavior

**Files:**
- Verify: `prototype/events.html`
- Verify: `prototype/events-b.html`
- Verify: `prototype/star.html`
- Verify: `prototype/follow-up-thread.html`

- [ ] **Step 1: Run automated tests**

Run: `pytest tests/test_event_center_shared.py -v`
Expected: PASS

- [ ] **Step 2: Check page loading and navigation**

Run: open the prototype pages in a browser and verify:
- Version A has embedded `特别关注 / 全部事件` tabs
- Version B has 4-tab bottom nav and no top tab switcher
- `star.html` shows flagged-only list and 4-tab nav
- card click still opens `follow-up-thread.html?fuId=...`

- [ ] **Step 3: Check interactive state changes**

Verify manually:
- starring opens inline deadline chooser
- choosing a deadline updates badge count and star fill
- cancelling star removes the event from flagged view
- closing an event dims it in all-events views and hides nothing from the all list
