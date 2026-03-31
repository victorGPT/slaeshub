"""Tests for 8-week regression mock data generator (v3)."""
import csv
import os
import subprocess
import pytest

CSV_PATH = "data/clients_simulation_v2.csv"

REQUIRED_FIELDS = [
    "uid","name",
    "w1","w2","w3","w4","w5","w6","w7","w8",
    "f_mean","trend_rate","r_squared","conf",
    "platform_trend_rate","adjusted_trend_rate",
    "churn_score","growth_score","status",
    "reason_tag","suggested_action",
    "has_futures","has_leverage","has_savings","has_card","has_cloud","has_mini",
    # Deposit distribution
    "dd_savings","dd_futures_margin","dd_spot_wallet","dd_card","dd_cloud",
    # Net contribution
    "nc_total","nc_futures","nc_leverage","nc_mini","nc_card","nc_cloud",
    "nc_savings_interest","nc_rebate","nc_wow",
    # Client P&L
    "pnl_7d_total","pnl_7d_futures","pnl_7d_leverage","pnl_7d_mini","pnl_7d_spot",
    "pnl_8w_weekly_avg",
    # Welfare fund
    "welfare_budget","welfare_sent","welfare_activated","welfare_remaining",
]


@pytest.fixture(scope="module", autouse=True)
def generate_csv():
    subprocess.run(["python3", "scripts/simulate_clients.py"],
                   check=True, cwd="/Users/victor/Developer/slaeshub")


def _load():
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


def test_csv_exists_and_has_100_rows():
    assert os.path.exists(CSV_PATH)
    assert len(_load()) == 100


def test_required_fields():
    with open(CSV_PATH) as f:
        fields = csv.DictReader(f).fieldnames
    for field in REQUIRED_FIELDS:
        assert field in fields, f"Missing: {field}"


def test_f_mean_positive():
    for row in _load():
        assert float(row["f_mean"]) > 0


def test_8_weeks_exist():
    for row in _load():
        for i in range(1, 9):
            assert float(row[f"w{i}"]) > 0


def test_status_values():
    valid = {"增长", "流失", "稳定"}
    for row in _load():
        assert row["status"] in valid


def test_conf_range():
    """Conf = 0.5 + 0.5*R-squared, so range is [0.5, 1.0]."""
    for row in _load():
        c = float(row["conf"])
        assert 0.5 <= c <= 1.0, f"Conf out of range: {c}"


def test_r_squared_range():
    for row in _load():
        r2 = float(row["r_squared"])
        assert 0 <= r2 <= 1.0


def test_churn_clients_have_positive_churn_score():
    for row in _load():
        if row["status"] == "流失":
            assert float(row["churn_score"]) > 0


def test_growth_clients_have_positive_growth_score():
    for row in _load():
        if row["status"] == "增长":
            assert float(row["growth_score"]) > 0


def test_stable_clients_have_zero_scores():
    for row in _load():
        if row["status"] == "稳定":
            assert float(row["churn_score"]) == 0
            assert float(row["growth_score"]) == 0


def test_platform_trend_consistent():
    rows = _load()
    trends = set(row["platform_trend_rate"] for row in rows)
    assert len(trends) == 1


def test_reason_and_action_not_empty():
    for row in _load():
        assert row["reason_tag"].strip()
        assert row["suggested_action"].strip()


def test_deposit_distribution_sums_to_f_mean():
    for row in _load():
        f_mean = float(row["f_mean"])
        dd_sum = sum(float(row[k]) for k in [
            "dd_savings","dd_futures_margin","dd_spot_wallet","dd_card","dd_cloud"])
        assert abs(dd_sum - f_mean) < 1.0, f"DD sum {dd_sum} != f_mean {f_mean}"


def test_deposit_distribution_non_negative():
    for row in _load():
        for k in ["dd_savings","dd_futures_margin","dd_spot_wallet","dd_card","dd_cloud"]:
            assert float(row[k]) >= 0


def test_net_contribution_total_equals_sum():
    for row in _load():
        parts = sum(float(row[k]) for k in [
            "nc_futures","nc_leverage","nc_mini","nc_card","nc_cloud",
            "nc_savings_interest","nc_rebate"])
        total = float(row["nc_total"])
        assert abs(total - parts) < 0.1, f"NC total {total} != sum {parts}"


def test_net_contribution_cost_modules_negative():
    for row in _load():
        assert float(row["nc_savings_interest"]) <= 0
        assert float(row["nc_rebate"]) <= 0


def test_pnl_7d_total_equals_sum():
    for row in _load():
        parts = sum(float(row[k]) for k in [
            "pnl_7d_futures","pnl_7d_leverage","pnl_7d_mini","pnl_7d_spot"])
        total = float(row["pnl_7d_total"])
        assert abs(total - parts) < 0.1


def test_pnl_spot_is_zero():
    """Spot P&L is placeholder, must be 0."""
    for row in _load():
        assert float(row["pnl_7d_spot"]) == 0


def test_welfare_remaining_equals_budget_minus_sent():
    for row in _load():
        budget = float(row["welfare_budget"])
        sent = float(row["welfare_sent"])
        remaining = float(row["welfare_remaining"])
        assert abs(remaining - (budget - sent)) < 0.1


def test_welfare_activated_leq_sent():
    for row in _load():
        assert float(row["welfare_activated"]) <= float(row["welfare_sent"]) + 0.01
