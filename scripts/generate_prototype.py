"""
Sales Hub MVP - Prototype Data Pipeline (v2)

读取 CSV → 构建 JSON → 输出 mock-data.js
"""
import csv
import sys
import os

# Allow import from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.prototype_data import build_mock_data, to_js

CSV_PATH = "data/clients_simulation_v2.csv"
OUTPUT = "prototype/mock-data.js"


def load():
    """Load CSV and return rows."""
    with open(CSV_PATH) as f:
        return list(csv.DictReader(f))


def main():
    rows = load()
    data = build_mock_data(rows)
    js = to_js(data)

    with open(OUTPUT, "w") as f:
        f.write(js)

    s = data["stats"]
    pt = data["platformTrendDisplay"]
    print(f"Generated {OUTPUT} ({len(js)} bytes)")
    print(f"  Platform trend: {pt}")
    print(f"  Total: {s['total']}  Churn: {s['churn']}  Growth: {s['growth']}  Stable: {s['stable']}")


if __name__ == "__main__":
    main()
