"""Tests for 8-week regression data contract (v3)."""
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


def test_top_level_keys(data):
    for k in ["generatedAt","clients","clientsById",
              "depositRankUids","churnUids","growthUids","stats",
              "events","eventsByClientUid"]:
        assert k in data


def test_client_count(data):
    assert len(data["clients"]) == 100


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
        assert len(c["weeks"]) == 8
        assert all(w > 0 for w in c["weeks"])


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


def test_trend_display_format(data):
    for c in data["clients"]:
        assert "/周" in c["trendDisplay"]


def test_trend_confidence_values(data):
    valid = {"趋势明确", "波动较大"}
    for c in data["clients"]:
        assert c["trendConfidence"] in valid


def test_deposit_dist_keys(data):
    required = {"savings", "futuresMargin", "spotWallet", "card", "cloud",
                "savingsDisplay", "futuresMarginDisplay", "spotWalletDisplay",
                "cardDisplay", "cloudDisplay"}
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


def test_events_list(data):
    assert isinstance(data["events"], list)
    assert len(data["events"]) > 0


def test_events_sorted_by_urgency(data):
    order = {"critical": 0, "warning": 1, "info": 2}
    urgencies = [order.get(e["urgency"], 9) for e in data["events"]]
    assert urgencies == sorted(urgencies)


def test_events_have_required_fields(data):
    required = {"id", "client_uid", "client_name", "type", "urgency", "color",
                "action", "time_ago", "task_state"}
    for evt in data["events"]:
        assert required.issubset(evt.keys()), f"Missing keys in event: {required - evt.keys()}"


def test_events_by_client_uid(data):
    assert isinstance(data["eventsByClientUid"], dict)
    for uid, evts in data["eventsByClientUid"].items():
        assert all(e["client_uid"] == uid for e in evts)


def test_stats_event_counts(data):
    s = data["stats"]
    assert "eventCount" in s
    assert s["eventCount"] == len(data["events"])
    assert "criticalEvents" in s


def test_churn_clients_have_events(data):
    """All churning clients should have at least one event."""
    for uid in data["churnUids"]:
        c = data["clientsById"][uid]
        assert len(c["events"]) > 0, f"Churn client {uid} has no events"


def test_growth_clients_have_events(data):
    """All growing clients should have at least one event."""
    for uid in data["growthUids"]:
        c = data["clientsById"][uid]
        assert len(c["events"]) > 0, f"Growth client {uid} has no events"
