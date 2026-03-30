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
              "depositRankUids","churnUids","growthUids","stats"]:
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
