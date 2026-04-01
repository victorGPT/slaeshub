"""Tests for 9-week regression data contract (v4 - events vs activities)."""
import csv
import pytest
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.prototype_data import build_mock_data

CSV_PATH = "data/clients_simulation_v2.csv"


def _load():
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def data():
    return build_mock_data(_load())


# --- Top-level structure ---

def test_top_level_keys(data):
    for k in ["generatedAt", "clients", "clientsById",
              "depositRankUids", "churnUids", "growthUids", "stats",
              "events", "eventsByClientUid",
              "activities", "activitiesByClientUid"]:
        assert k in data


def test_client_count(data):
    assert len(data["clients"]) == 100


# --- Client card fields ---

def test_card_fields(data):
    for c in data["clients"]:
        assert "depositDisplay" in c
        assert "status" in c
        assert "reasonTag" in c
        assert "suggestedAction" in c
        assert "trendDisplay" in c
        assert "trendConfidence" in c


def test_weeks_array(data):
    for c in data["clients"]:
        assert len(c["weeks"]) == 9
        assert all(w > 0 for w in c["weeks"])


# --- Ranking views ---

def test_deposit_rank_sorted(data):
    uids = data["depositRankUids"]
    vals = [data["clientsById"][u]["fMean"] for u in uids]
    assert vals == sorted(vals, reverse=True)


def test_churn_sorted(data):
    uids = data["churnUids"]
    scores = [data["clientsById"][u]["churnScore"] for u in uids]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)


def test_growth_sorted(data):
    uids = data["growthUids"]
    scores = [data["clientsById"][u]["growthScore"] for u in uids]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)


def test_stats(data):
    s = data["stats"]
    assert s["total"] == 100
    assert s["churn"] == len(data["churnUids"])
    assert s["growth"] == len(data["growthUids"])


# --- Display formatting ---

def test_trend_display_format(data):
    for c in data["clients"]:
        assert "/周" in c["trendDisplay"]


def test_trend_confidence_values(data):
    valid = {"趋势明确", "波动较大"}
    for c in data["clients"]:
        assert c["trendConfidence"] in valid


# --- Detail fields ---

def test_deposit_dist_keys(data):
    required = {"futures", "leverage", "savings", "card", "cloud", "mini", "spot",
                "futuresDisplay", "leverageDisplay", "savingsDisplay",
                "cardDisplay", "cloudDisplay", "miniDisplay", "spotDisplay"}
    for c in data["clients"]:
        assert "depositDist" in c
        assert required.issubset(c["depositDist"].keys())


def test_net_contribution_keys(data):
    required = {"total", "totalDisplay", "futures", "leverage", "mini",
                "card", "cloud", "savingsInterest", "rebate", "wow", "wowDisplay"}
    for c in data["clients"]:
        assert "netContribution" in c
        assert required.issubset(c["netContribution"].keys())


def test_client_pnl_keys(data):
    required = {"total7d", "futures7d", "leverage7d", "mini7d", "spot7d", "weeklyAvg8w"}
    for c in data["clients"]:
        assert "clientPnl" in c
        assert required.issubset(c["clientPnl"].keys())


def test_pnl_format(data):
    """Each P&L entry should have value, display, and color."""
    c = data["clients"][0]
    pnl = c["clientPnl"]["total7d"]
    assert "value" in pnl
    assert "display" in pnl
    assert "color" in pnl


def test_welfare_keys(data):
    required = {"budget", "sent", "activated", "remaining",
                "budgetDisplay", "sentDisplay", "activatedDisplay", "remainingDisplay"}
    for c in data["clients"]:
        assert "welfare" in c
        assert required.issubset(c["welfare"].keys())


# --- Events (homepage, action required) ---

VALID_EVENT_TYPES = {'风控触发', '超大额出金', '爆仓'}


def test_events_list(data):
    assert isinstance(data["events"], list)
    assert len(data["events"]) > 0


def test_events_only_three_types(data):
    """Events pushed to homepage must only be one of 3 types."""
    for evt in data["events"]:
        assert evt["type"] in VALID_EVENT_TYPES, \
            f"Unexpected event type: {evt['type']}"


def test_events_all_critical(data):
    """All events should be critical urgency."""
    for evt in data["events"]:
        assert evt["urgency"] == "critical"
        assert evt["color"] == "#F6465D"


def test_events_sorted_by_urgency(data):
    order = {"critical": 0, "warning": 1, "info": 2}
    urgencies = [order.get(e["urgency"], 9) for e in data["events"]]
    assert urgencies == sorted(urgencies)


def test_events_have_required_fields(data):
    required = {"id", "client_uid", "client_name", "type", "urgency", "color",
                "action", "time_ago", "task_state", "sub_type", "expires_in"}
    for evt in data["events"]:
        assert required.issubset(evt.keys()), \
            f"Missing keys in event: {required - evt.keys()}"


def test_events_expires_in(data):
    """Verify expires_in values per event type."""
    for evt in data["events"]:
        if evt["type"] == "风控触发":
            assert evt["expires_in"] is None
        elif evt["type"] == "超大额出金":
            assert evt["expires_in"] == "48小时"
        elif evt["type"] == "爆仓":
            assert evt["expires_in"] == "72小时"


def test_events_by_client_uid(data):
    assert isinstance(data["eventsByClientUid"], dict)
    for uid, evts in data["eventsByClientUid"].items():
        assert all(e["client_uid"] == uid for e in evts)


def test_events_count_reasonable(data):
    """With 100 clients, expect roughly 5-25 events (not 80+)."""
    count = len(data["events"])
    assert count < 50, f"Too many events ({count}), should be < 50"
    assert count >= 3, f"Too few events ({count}), expected at least 3"


def test_stats_event_counts(data):
    s = data["stats"]
    assert "eventCount" in s
    assert s["eventCount"] == len(data["events"])
    assert "criticalEvents" in s
    assert s["criticalEvents"] == len(data["events"])  # all events are critical


# --- Mega withdraw threshold ---

def test_mega_withdraw_threshold(data):
    """超大额出金 amount must be >= 30% of client fMean."""
    for evt in data["events"]:
        if evt["type"] == "超大额出金":
            uid = evt["client_uid"]
            f_mean = data["clientsById"][uid]["fMean"]
            assert abs(evt["amount"]) >= f_mean * 0.3 - 1, \
                f"Mega withdraw {abs(evt['amount']):.0f} < 30% of fMean {f_mean:.0f}"


# --- Liquidation event ---

def test_liquidation_sub_types(data):
    """爆仓 sub_type must be 合约爆仓 or 杠杆爆仓."""
    valid = {'合约爆仓', '杠杆爆仓'}
    for evt in data["events"]:
        if evt["type"] == "爆仓":
            assert evt["sub_type"] in valid


def test_liquidation_clients_have_futures_or_leverage(data):
    """爆仓 events only for clients with futures or leverage."""
    for evt in data["events"]:
        if evt["type"] == "爆仓":
            uid = evt["client_uid"]
            c = data["clientsById"][uid]
            biz = c["bizLines"]
            assert "合约" in biz or "杠杆" in biz, \
                f"Client {uid} has liquidation but no futures/leverage"


# --- Activities (client detail only) ---

VALID_ACTIVITY_TYPES = {'大额出金', '大额入金', '理财到期', '大额盈利', '大额亏损'}


def test_activities_list(data):
    assert isinstance(data["activities"], list)
    assert len(data["activities"]) > 0


def test_activities_only_valid_types(data):
    for act in data["activities"]:
        assert act["type"] in VALID_ACTIVITY_TYPES, \
            f"Unexpected activity type: {act['type']}"


def test_activities_have_required_fields(data):
    required = {"id", "client_uid", "client_name", "type", "sub_type",
                "amount_display", "time_ago"}
    for act in data["activities"]:
        assert required.issubset(act.keys()), \
            f"Missing keys in activity: {required - act.keys()}"


def test_activities_no_event_fields(data):
    """Activities should NOT have urgency, task_state, action, script."""
    event_only = {"urgency", "task_state", "action", "script"}
    for act in data["activities"]:
        overlap = event_only & act.keys()
        assert not overlap, f"Activity has event-only fields: {overlap}"


def test_activities_by_client_uid(data):
    assert isinstance(data["activitiesByClientUid"], dict)
    for uid, acts in data["activitiesByClientUid"].items():
        assert all(a["client_uid"] == uid for a in acts)


def test_activities_count_reasonable(data):
    """With 100 clients, expect 30-80 activities."""
    count = len(data["activities"])
    assert count >= 20, f"Too few activities ({count})"
    assert count < 150, f"Too many activities ({count})"


def test_stats_activity_count(data):
    s = data["stats"]
    assert "activityCount" in s
    assert s["activityCount"] == len(data["activities"])


# --- Client-level events & activities ---

def test_clients_have_events_and_activities(data):
    """Each client should have events and activities lists."""
    for c in data["clients"]:
        assert "events" in c
        assert "activities" in c
        assert isinstance(c["events"], list)
        assert isinstance(c["activities"], list)
