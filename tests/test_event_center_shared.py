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
      {{ fuId: 'fu_1', deadline: 'month', flaggedAt: '2026-04-03T08:00:00Z' }},
      {{ fuId: 'fu_2', deadline: 'today', flaggedAt: '2026-04-02T08:00:00Z' }}
    ];
    const result = shared.computeFlaggedView(events, flagged, ['fu_1']);
    console.log(JSON.stringify(result));
    """
    result = run_node(script)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert [row["id"] for row in payload["items"]] == ["fu_2", "fu_1"]
    assert payload["items"][0]["deadlineLabel"] == "本日"
    assert payload["items"][0]["deadlineColor"] == "#F6465D"
    assert payload["items"][1]["isClosed"] is True


def test_compute_all_view_filters_types_and_exposes_flagged_count():
    script = f"""
    const shared = require({json.dumps(str(MODULE))});
    const events = [
      {{ id: 'fu_1', title: 'A', type: '主动联系', client_name: '甲', created_at: '2026-04-01T10:00:00Z', status: '跟进中' }},
      {{ id: 'fu_2', title: 'B', type: '客户反馈', client_name: '乙', created_at: '2026-04-03T10:00:00Z', status: '跟进中' }},
      {{ id: 'fu_3', title: 'C', type: '主动联系', client_name: '丙', created_at: '2026-04-02T10:00:00Z', status: '跟进中' }}
    ];
    const flagged = [
      {{ fuId: 'fu_2', deadline: 'today', flaggedAt: '2026-04-02T08:00:00Z' }},
      {{ fuId: 'fu_3', deadline: 'week', flaggedAt: '2026-04-02T09:00:00Z' }}
    ];
    const result = shared.computeAllView(events, flagged, ['fu_1'], '主动联系');
    console.log(JSON.stringify(result));
    """
    result = run_node(script)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["flaggedCount"] == 2
    assert payload["flaggedBadgeVisible"] is True
    assert [row["id"] for row in payload["items"]] == ["fu_3", "fu_1"]
    assert payload["items"][0]["isFlagged"] is True
    assert payload["items"][1]["isClosed"] is True


def test_upsert_and_remove_flagged_entry_and_close_event_ids():
    script = f"""
    const shared = require({json.dumps(str(MODULE))});
    let flagged = [];
    flagged = shared.upsertFlaggedEntry(flagged, 'fu_1', 'today', '2026-04-03T09:00:00Z');
    flagged = shared.upsertFlaggedEntry(flagged, 'fu_1', 'week', '2026-04-03T10:00:00Z');
    flagged = shared.upsertFlaggedEntry(flagged, 'fu_2', 'month', '2026-04-03T11:00:00Z');
    flagged = shared.removeFlaggedEntry(flagged, 'fu_1');
    const closed = shared.closeEventIds(['fu_2'], 'fu_2');
    console.log(JSON.stringify({{ flagged, closed, badge: shared.getFlaggedBadgeMeta(flagged) }}));
    """
    result = run_node(script)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["flagged"] == [
        {"fuId": "fu_2", "deadline": "month", "flaggedAt": "2026-04-03T11:00:00Z"}
    ]
    assert payload["closed"] == ["fu_2"]
    assert payload["badge"] == {"count": 1, "visible": True, "text": "1"}
