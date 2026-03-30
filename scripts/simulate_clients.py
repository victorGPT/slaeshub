"""
Sales Hub MVP - Mock Client Data Generator (v3)

8-week linear regression trend + log-compressed scoring.
Source of truth: docs/product-concept-v2.md S4-5
"""
import csv
import math
import random

random.seed(42)

N = 100
OUTPUT = "data/clients_simulation_v2.csv"

# Thresholds
T_F_PERCENTILE = 0.80
DELTA = 0.02  # 2%/week

# Names
SURNAMES = ["张","李","王","刘","陈","杨","赵","黄","周","吴",
            "徐","孙","胡","朱","高","林","何","郭","马","罗"]
GIVEN_NAMES = ["伟","芳","娜","敏","强","磊","洋","勇","军","杰",
               "涛","明","超","秀英","华","丽","静","建国","文","志强"]

# Reason/action pools
CHURN_REASONS = ["理财到期/赎回","近期连续出金","长时间未登录","U卡场景绑定弱","权益不足/续存未触达"]
GROWTH_REASONS = ["近期持续入金","理财续存","积分活动参与","卡场景开始渗透","平台活跃提升"]
STABLE_REASONS = ["高资沉、稳定沉淀","资沉高、场景关系浅","资沉高、近期有增长机会"]
CHURN_ACTIONS = ["安排销售回访","续存提醒+权益说明","资沉补贴券"]
GROWTH_ACTIONS = ["推荐U卡积分活动","场景绑定说明","续存提醒+权益说明"]
STABLE_ACTIONS = ["推荐U卡积分活动","场景绑定说明","安排销售回访"]

BIZ_LINES = ["futures","leverage","savings","card","cloud","mini"]

FIELDS = [
    "uid","name",
    "w1","w2","w3","w4","w5","w6","w7","w8",
    "f_mean","trend_rate","r_squared","conf",
    "platform_trend_rate","adjusted_trend_rate",
    "churn_score","growth_score","status",
    "reason_tag","suggested_action",
    "has_futures","has_leverage","has_savings","has_card","has_cloud","has_mini",
]


def _linreg(ys):
    """Linear regression on t=[1..n] vs ys. Returns (slope, r_squared)."""
    n = len(ys)
    t_mean = (n + 1) / 2.0
    y_mean = sum(ys) / n

    num = sum((i + 1 - t_mean) * (y - y_mean) for i, y in enumerate(ys))
    den = sum((i + 1 - t_mean) ** 2 for i in range(n))

    b = num / den if den != 0 else 0.0

    # R-squared
    ss_res = sum((y - (y_mean + b * (i + 1 - t_mean))) ** 2 for i, y in enumerate(ys))
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    r2 = max(0.0, min(1.0, r2))

    return b, r2


def _generate_weekly_series(base_level, trend_type, noise_std=0.05):
    """Generate 8 weekly deposit values with a trend pattern."""
    weeks = []
    for t in range(8):
        if trend_type == "churn":
            drift = -random.uniform(0.01, 0.06) * (t + 1)
        elif trend_type == "growth":
            drift = random.uniform(0.01, 0.05) * (t + 1)
        else:
            drift = random.uniform(-0.02, 0.02) * (t + 1)

        noise = random.gauss(0, noise_std)
        weeks.append(base_level * (1 + drift + noise))

    return [max(w, 1000) for w in weeks]  # floor at 1000 USDT


def generate():
    # Platform trend: 8 weekly values for the whole platform
    platform_base = 1e9
    platform_roll = random.random()
    if platform_roll < 0.3:
        platform_type = "churn"
    elif platform_roll < 0.5:
        platform_type = "growth"
    else:
        platform_type = "stable"

    platform_weeks = _generate_weekly_series(platform_base, platform_type, noise_std=0.02)
    platform_b, platform_r2 = _linreg(platform_weeks)
    platform_mean = sum(platform_weeks) / 8
    platform_trend_rate = platform_b / platform_mean if platform_mean > 0 else 0

    clients = []
    for _ in range(N):
        base = math.exp(random.gauss(15.4, 1.8))  # median ~5M USDT

        # Assign trend type
        roll = random.random()
        if roll < 0.20:
            trend_type = "churn"
        elif roll < 0.40:
            trend_type = "growth"
        else:
            trend_type = "stable"

        weeks = _generate_weekly_series(base, trend_type)
        b, r2 = _linreg(weeks)
        f_mean = sum(weeks) / 8
        trend_rate = b / f_mean if f_mean > 0 else 0
        adjusted = trend_rate - platform_trend_rate
        conf = 0.5 + 0.5 * r2

        # Business lines
        prob = 0.7 if f_mean > 1e7 else (0.4 if f_mean > 1e6 else 0.15)
        biz = {f"has_{line}": random.random() < prob for line in BIZ_LINES}

        clients.append({
            "uid": str(random.randint(10_000_000, 99_999_999)),
            "name": random.choice(SURNAMES) + random.choice(GIVEN_NAMES),
            "weeks": weeks,
            "f_mean": f_mean,
            "trend_rate": trend_rate,
            "r_squared": r2,
            "conf": conf,
            "platform_trend_rate": platform_trend_rate,
            "adjusted_trend_rate": adjusted,
            **biz,
        })

    return _score(clients)


def _score(clients):
    """Compute ChurnScore / GrowthScore and assign status."""
    sorted_f = sorted(clients, key=lambda c: c["f_mean"])
    t_f = sorted_f[int(len(sorted_f) * T_F_PERCENTILE)]["f_mean"]

    for c in clients:
        f = c["f_mean"]
        adj = c["adjusted_trend_rate"]
        conf = c["conf"]

        log_f = math.log(1 + f / t_f)

        churn_factor = max(0.0, -adj - DELTA)
        growth_factor = max(0.0, adj - DELTA)

        c["churn_score"] = log_f * churn_factor * conf
        c["growth_score"] = log_f * growth_factor * conf

        # Status: churn wins if both > 0
        if c["churn_score"] > 0:
            c["status"] = "流失"
            c["reason_tag"] = random.choice(CHURN_REASONS)
            c["suggested_action"] = random.choice(CHURN_ACTIONS)
        elif c["growth_score"] > 0:
            c["status"] = "增长"
            c["reason_tag"] = random.choice(GROWTH_REASONS)
            c["suggested_action"] = random.choice(GROWTH_ACTIONS)
        else:
            c["status"] = "稳定"
            c["reason_tag"] = random.choice(STABLE_REASONS)
            c["suggested_action"] = random.choice(STABLE_ACTIONS)

    return clients


def write_csv(clients):
    with open(OUTPUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for c in clients:
            row = {}
            for k in FIELDS:
                if k in ("w1","w2","w3","w4","w5","w6","w7","w8"):
                    idx = int(k[1]) - 1
                    row[k] = f"{c['weeks'][idx]:.2f}"
                elif k == "f_mean":
                    row[k] = f"{c[k]:.2f}"
                elif k in ("churn_score","growth_score"):
                    row[k] = f"{c[k]:.6f}"
                elif k in ("trend_rate","r_squared","conf","platform_trend_rate","adjusted_trend_rate"):
                    row[k] = f"{c[k]:.6f}"
                elif isinstance(c.get(k), bool):
                    row[k] = "1" if c[k] else "0"
                else:
                    row[k] = str(c.get(k, ""))
            w.writerow(row)


def main():
    clients = generate()
    write_csv(clients)

    churn = sum(1 for c in clients if c["status"] == "流失")
    growth = sum(1 for c in clients if c["status"] == "增长")
    stable = sum(1 for c in clients if c["status"] == "稳定")
    pt = clients[0]["platform_trend_rate"]
    print(f"Generated {N} clients -> {OUTPUT}")
    print(f"  Platform TrendRate: {pt:+.4f}/week")
    print(f"  流失: {churn}  增长: {growth}  稳定: {stable}")


if __name__ == "__main__":
    main()
