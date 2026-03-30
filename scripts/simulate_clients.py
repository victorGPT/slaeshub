"""
Sales Hub MVP - Mock Client Data Generator (v2)

数据模型以资金沉淀（F）为北极星指标。
核心字段: F_base, F_recent, AdjustedTrend_F, 双门槛入池。
约束条件来源: MVP 方案补充约束版 S17。
"""
import csv
import math
import random

random.seed(42)

N = 100
OUTPUT = "data/clients_simulation_v2.csv"

# --- 阈值 ---
T_F_PERCENTILE = 0.80   # 重点客户门槛（P80）
DELTA = 0.10             # 相对变化阈值 (10%)
T_DROP = 50_000          # 绝对流失门槛 (5 万 USDT)
T_GROWTH = 50_000        # 绝对增长门槛 (5 万 USDT)

# --- 中文姓名池 ---
SURNAMES = [
    "张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
    "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗",
]
GIVEN_NAMES = [
    "伟", "芳", "娜", "敏", "强", "磊", "洋", "勇", "军", "杰",
    "涛", "明", "超", "秀英", "华", "丽", "静", "建国", "文", "志强",
]

# --- 原因标签池 ---
CHURN_REASONS = [
    "理财到期/赎回", "近期连续出金", "长时间未登录",
    "U卡场景绑定弱", "权益不足/续存未触达",
]
GROWTH_REASONS = [
    "近期持续入金", "理财续存", "积分活动参与",
    "卡场景开始渗透", "平台活跃提升",
]
STABLE_REASONS = [
    "高资沉、稳定沉淀", "资沉高、场景关系浅",
    "资沉高、近期有增长机会",
]

# --- 动作白名单 ---
CHURN_ACTIONS = ["安排销售回访", "续存提醒+权益说明", "资沉补贴券"]
GROWTH_ACTIONS = ["推荐U卡积分活动", "场景绑定说明", "续存提醒+权益说明"]
STABLE_ACTIONS = ["推荐U卡积分活动", "场景绑定说明", "安排销售回访"]

# --- 业务线 ---
BIZ_LINES = ["futures", "leverage", "savings", "card", "cloud", "mini"]

FIELDS = [
    "uid", "name", "f_base", "f_recent",
    "trend_f", "platform_trend", "adjusted_trend_f", "abs_change",
    "status", "churn_priority", "growth_priority",
    "reason_tag", "suggested_action",
    "has_futures", "has_leverage", "has_savings",
    "has_card", "has_cloud", "has_mini",
]


def _lognormal(mu: float, sigma: float) -> float:
    return math.exp(random.gauss(mu, sigma))


def _name() -> str:
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)


def _uid() -> str:
    return str(random.randint(10_000_000, 99_999_999))


def _biz_flags(f_base: float) -> dict:
    """业务线参与概率随资沉递增。"""
    if f_base > 1e7:
        prob = 0.7
    elif f_base > 1e6:
        prob = 0.4
    else:
        prob = 0.15
    return {f"has_{line}": random.random() < prob for line in BIZ_LINES}


def generate() -> list[dict]:
    # 模拟平台整体趋势（如近期市场微跌）
    platform_trend = round(random.uniform(-0.08, 0.05), 4)

    clients: list[dict] = []
    for _ in range(N):
        f_base = _lognormal(15.4, 1.8)  # median ~5M USDT

        # 客户个体趋势 = 市场 + 个体行为
        roll = random.random()
        if roll < 0.25:
            individual = -random.uniform(0.05, 0.50)
        elif roll < 0.50:
            individual = random.uniform(0.05, 0.60)
        else:
            individual = random.uniform(-0.04, 0.04)

        trend_f = platform_trend + individual
        f_recent = f_base * (1 + trend_f)
        abs_change = f_recent - f_base
        adjusted = trend_f - platform_trend  # == individual

        clients.append({
            "uid": _uid(),
            "name": _name(),
            "f_base": f_base,
            "f_recent": f_recent,
            "trend_f": trend_f,
            "platform_trend": platform_trend,
            "adjusted_trend_f": adjusted,
            "abs_change": abs_change,
            **_biz_flags(f_base),
        })

    return _classify(clients)


def _classify(clients: list[dict]) -> list[dict]:
    """双门槛分类 + 排序分 + 标签。"""
    sorted_f = sorted(clients, key=lambda c: c["f_base"])
    t_f = sorted_f[int(len(sorted_f) * T_F_PERCENTILE)]["f_base"]

    for c in clients:
        adj = c["adjusted_trend_f"]
        absc = abs(c["abs_change"])

        is_churn = (c["f_base"] >= t_f and adj <= -DELTA and absc >= T_DROP)
        is_growth = (c["f_base"] >= t_f and adj >= DELTA and absc >= T_GROWTH)

        if is_churn:
            c["status"] = "流失"
            c["churn_priority"] = c["f_base"] * abs(adj)
            c["growth_priority"] = 0.0
            c["reason_tag"] = random.choice(CHURN_REASONS)
            c["suggested_action"] = random.choice(CHURN_ACTIONS)
        elif is_growth:
            c["status"] = "增长"
            c["churn_priority"] = 0.0
            c["growth_priority"] = c["f_base"] * adj
            c["reason_tag"] = random.choice(GROWTH_REASONS)
            c["suggested_action"] = random.choice(GROWTH_ACTIONS)
        else:
            c["status"] = "稳定"
            c["churn_priority"] = 0.0
            c["growth_priority"] = 0.0
            c["reason_tag"] = random.choice(STABLE_REASONS)
            c["suggested_action"] = random.choice(STABLE_ACTIONS)

    return clients


RATIO_FIELDS = {"trend_f", "platform_trend", "adjusted_trend_f"}


def write_csv(clients: list[dict]) -> None:
    with open(OUTPUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for c in clients:
            row = {}
            for k in FIELDS:
                v = c[k]
                if isinstance(v, bool):
                    row[k] = "1" if v else "0"
                elif isinstance(v, float):
                    row[k] = f"{v:.6f}" if k in RATIO_FIELDS else f"{v:.2f}"
                else:
                    row[k] = str(v)
            w.writerow(row)


def main():
    clients = generate()
    write_csv(clients)

    churn = sum(1 for c in clients if c["status"] == "流失")
    growth = sum(1 for c in clients if c["status"] == "增长")
    stable = sum(1 for c in clients if c["status"] == "稳定")
    pt = clients[0]["platform_trend"]
    print(f"Generated {N} clients -> {OUTPUT}")
    print(f"  Platform trend: {pt:+.2%}")
    print(f"  流失: {churn}  增长: {growth}  稳定: {stable}")


if __name__ == "__main__":
    main()
