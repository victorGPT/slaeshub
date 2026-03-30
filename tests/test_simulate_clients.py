"""Tests for deposit-centric mock data generator (v2)."""
import csv
import os
import subprocess
import pytest

CSV_PATH = "data/clients_simulation_v2.csv"

REQUIRED_FIELDS = [
    "uid", "name",
    "f_base", "f_recent",
    "trend_f", "platform_trend", "adjusted_trend_f",
    "abs_change",
    "status",
    "churn_priority", "growth_priority",
    "reason_tag", "suggested_action",
    "has_futures", "has_leverage", "has_savings",
    "has_card", "has_cloud", "has_mini",
]


@pytest.fixture(scope="module", autouse=True)
def generate_csv():
    """Run the generator once before all tests."""
    subprocess.run(["python3", "scripts/simulate_clients.py"], check=True, cwd="/Users/victor/Developer/slaeshub")
    yield


def _load_rows():
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


def test_csv_exists_and_has_100_rows():
    assert os.path.exists(CSV_PATH)
    rows = _load_rows()
    assert len(rows) == 100


def test_csv_has_required_fields():
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
    for field in REQUIRED_FIELDS:
        assert field in fields, f"Missing field: {field}"


def test_f_base_positive():
    for row in _load_rows():
        assert float(row["f_base"]) > 0


def test_status_values():
    valid = {"增长", "流失", "稳定"}
    for row in _load_rows():
        assert row["status"] in valid, f"Invalid status: {row['status']}"


def test_churn_clients_have_negative_adjusted_trend():
    for row in _load_rows():
        if row["status"] == "流失":
            assert float(row["adjusted_trend_f"]) < 0
            assert abs(float(row["abs_change"])) > 0


def test_growth_clients_have_positive_adjusted_trend():
    for row in _load_rows():
        if row["status"] == "增长":
            assert float(row["adjusted_trend_f"]) > 0
            assert float(row["abs_change"]) > 0


def test_platform_trend_consistent():
    """All rows should have the same platform_trend (single simulation run)."""
    rows = _load_rows()
    trends = set(row["platform_trend"] for row in rows)
    assert len(trends) == 1


def test_reason_tag_not_empty():
    for row in _load_rows():
        assert row["reason_tag"].strip() != ""


def test_suggested_action_not_empty():
    for row in _load_rows():
        assert row["suggested_action"].strip() != ""


def test_churn_priority_formula():
    """ChurnPriority = F_base * |AdjustedTrend_F| for churn clients."""
    for row in _load_rows():
        if row["status"] == "流失":
            expected = float(row["f_base"]) * abs(float(row["adjusted_trend_f"]))
            actual = float(row["churn_priority"])
            # Allow 0.01% relative tolerance for CSV rounding
            tol = max(expected * 1e-4, 1.0)
            assert abs(actual - expected) < tol, f"ChurnPriority mismatch: {actual} vs {expected}"


def test_growth_priority_formula():
    """GrowthPriority = F_base * AdjustedTrend_F for growth clients."""
    for row in _load_rows():
        if row["status"] == "增长":
            expected = float(row["f_base"]) * float(row["adjusted_trend_f"])
            actual = float(row["growth_priority"])
            tol = max(expected * 1e-4, 1.0)
            assert abs(actual - expected) < tol, f"GrowthPriority mismatch: {actual} vs {expected}"
