"""Tests for deposit-centric data contract (v2)."""
import csv
import pytest
import sys
import os

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
    for key in ["generatedAt", "clients", "clientsById",
                "depositRankUids", "churnUids", "growthUids", "stats"]:
        assert key in data, f"Missing key: {key}"


def test_client_count(data):
    assert len(data["clients"]) == 100


def test_client_card_fields(data):
    """每个客户包含卡片所需的四项信息。"""
    for c in data["clients"]:
        assert "depositDisplay" in c
        assert "status" in c
        assert "reasonTag" in c
        assert "suggestedAction" in c


def test_deposit_rank_sorted(data):
    """资沉总量视图按 F_base 降序。"""
    uids = data["depositRankUids"]
    deposits = [data["clientsById"][uid]["fBase"] for uid in uids]
    assert deposits == sorted(deposits, reverse=True)


def test_churn_sorted(data):
    """流失视图按 ChurnPriority 降序。"""
    uids = data["churnUids"]
    priorities = [data["clientsById"][uid]["churnPriority"] for uid in uids]
    assert priorities == sorted(priorities, reverse=True)


def test_growth_sorted(data):
    """增长视图按 GrowthPriority 降序。"""
    uids = data["growthUids"]
    priorities = [data["clientsById"][uid]["growthPriority"] for uid in uids]
    assert priorities == sorted(priorities, reverse=True)


def test_churn_uids_all_have_churn_status(data):
    for uid in data["churnUids"]:
        assert data["clientsById"][uid]["status"] == "流失"


def test_growth_uids_all_have_growth_status(data):
    for uid in data["growthUids"]:
        assert data["clientsById"][uid]["status"] == "增长"


def test_stats_consistent(data):
    s = data["stats"]
    assert s["total"] == 100
    assert s["churn"] == len(data["churnUids"])
    assert s["growth"] == len(data["growthUids"])
    assert s["stable"] == 100 - s["churn"] - s["growth"]


def test_detail_href(data):
    for c in data["clients"]:
        assert c["detailHref"] == f"client-detail.html?uid={c['uid']}"
