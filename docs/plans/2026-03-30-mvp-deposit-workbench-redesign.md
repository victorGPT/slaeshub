# Sales Hub MVP 重构：以资金沉淀为北极星的销售工作台

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 Sales Hub 原型从"高价值/高潜力客户分类"体系，彻底重构为"资沉总量/资沉流失/资沉增长"三视图销售工作台。

**Architecture:** 保持纯静态 HTML + Tailwind CDN + vanilla JS 架构不变。重写 Python mock 数据生成管线以匹配新数据模型（F_base / F_recent / AdjustedTrend_F / 双门槛入池）。首页从多版本（A/B/C）收敛为单一页面 + 三个 Tab 筛选。客户卡片精简为四项信息（资沉总量、近期状态、原因标签、建议动作）。

**Tech Stack:** HTML5, Tailwind CSS (CDN), vanilla JavaScript, Python 3 (stdlib only)

**需求来源:**
- `/Users/victor/trae_projects/tabataX/文档/A交易所_销售系统MVP方案_资沉总量_流失_增长.md`
- `/Users/victor/trae_projects/tabataX/文档/A交易所_销售系统MVP方案_资沉总量_流失_增长_补充约束版.md`（第 17 节约束条件）

**当前原型:** `/Users/victor/Developer/slaeshub/prototype/`

---

## 变更总览

| 维度 | 旧 (高价值/高潜力) | 新 (资沉三视图) |
|------|-------------------|----------------|
| 首页结构 | 3 个版本 (A/B/C)，双榜 | 1 个页面，3 个 Tab |
| 主指标 | N90, F90, E90 | F_base (USDT), AdjustedTrend_F |
| 客户分类 | 高价值 / 高潜 / 非主榜 | 总量 / 流失 / 增长 / 稳定 |
| 入池规则 | 分位数阈值 | 双门槛（相对% + 绝对金额） |
| 市场修正 | 无 | 平台基准修正（AdjustedTrend_F = Trend_F - PlatformTrend） |
| 卡片信息 | 名字、标签、贡献、趋势、AI建议 | 资沉总量、近期状态、原因标签、建议动作 |
| 排序 | N90 / 机会缺口 | F_base / ChurnPriority / GrowthPriority |
| 客户详情 | N90 为核心的 360 仪表盘 | 资沉为核心 + 流失/增长趋势 |

---

## Task 1: 更新产品文档

**Files:**
- Create: `docs/product-concept-v2.md`
- Archive: `docs/product-concept.md` → `docs/archive/product-concept-v1.md`
- Archive: `docs/主动观察核心字段计算公式及确认清单.md` → `docs/archive/`
- Archive: `docs/主动观察榜单定义.md` → `docs/archive/`

**Step 1: 创建 archive 目录，迁移旧文档**

```bash
mkdir -p docs/archive
mv docs/product-concept.md docs/archive/product-concept-v1.md
mv docs/主动观察核心字段计算公式及确认清单.md docs/archive/
mv docs/主动观察榜单定义.md docs/archive/
```

**Step 2: 创建新产品文档 `docs/product-concept-v2.md`**

内容要点（从 MVP 方案稿浓缩）：

```markdown
# Sales Hub 产品概念 v2

## 北极星指标
F = 客户在平台的总资金沉淀（折 USDT，每日 UTC 00:00 快照）

## 前台结构
一个主列表 + 两个快捷筛选 Tab：
- Tab 1: 资沉总量（默认，按 F_base 降序）
- Tab 2: 资沉流失（双门槛: AdjustedTrend_F <= -δ 且 AbsoluteDrop >= T_drop）
- Tab 3: 资沉增长（双门槛: AdjustedTrend_F >= δ 且 AbsoluteGrowth >= T_growth）

## 市场修正
AdjustedTrend_F = Trend_F - PlatformTrend
只有跑输/跑赢平台整体的客户才算真实流失/增长

## 客户卡片
四项信息：资沉总量、近期状态、原因标签、建议动作

## 排序公式
- DepositRank = F_base
- ChurnPriority = F_base × |AdjustedTrend_F|
- GrowthPriority = F_base × AdjustedTrend_F

## 动作约束
- 冷却: 同类动作 7 天内不重复
- 互斥: 同一时点只有一个主动作
- 留痕: 每次动作记录前状态 + 事件 + 7/30 天后结果

## 不做清单
不做高价值/高潜分类、不做复杂画像、不做多动作推荐、不做 AI 归因
```

**Step 3: 更新 README.md 中的 Fact Sources 引用**

将所有引用 `product-concept.md` 的地方改为 `product-concept-v2.md`。

**Step 4: Commit**

```bash
git add docs/ README.md
git commit -m "docs: archive v1 product docs, create v2 product concept (deposit-centric)"
```

---

## Task 2: 重写 Mock 数据模型

**Files:**
- Rewrite: `scripts/simulate_clients.py`
- Test: `tests/test_simulate_clients.py`

**Step 1: 写测试 `tests/test_simulate_clients.py`**

```python
import csv
import os
import subprocess
import pytest

CSV_PATH = "data/clients_simulation_v2.csv"

REQUIRED_FIELDS = [
    "uid", "name",
    "f_base", "f_recent",
    "trend_f", "platform_trend", "adjusted_trend_f",
    "abs_change",      # 绝对金额变化
    "status",          # "增长" | "流失" | "稳定"
    "churn_priority", "growth_priority",
    "reason_tag", "suggested_action",
    # 业务线参与度（简化版）
    "has_futures", "has_leverage", "has_savings",
    "has_card", "has_cloud", "has_mini",
]

def test_csv_generated():
    """CSV 文件存在且非空"""
    subprocess.run(["python3", "scripts/simulate_clients.py"], check=True)
    assert os.path.exists(CSV_PATH)
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 100

def test_csv_has_required_fields():
    """CSV 包含所有必需字段"""
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
    for field in REQUIRED_FIELDS:
        assert field in fields, f"Missing field: {field}"

def test_f_base_positive():
    """F_base 全部为正数"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            assert float(row["f_base"]) > 0

def test_status_values():
    """Status 只有三种合法值"""
    valid = {"增长", "流失", "稳定"}
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            assert row["status"] in valid, f"Invalid status: {row['status']}"

def test_churn_clients_have_negative_adjusted_trend():
    """流失客户的 AdjustedTrend_F 必须为负且绝对变化超门槛"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            if row["status"] == "流失":
                assert float(row["adjusted_trend_f"]) < 0
                assert abs(float(row["abs_change"])) > 0

def test_growth_clients_have_positive_adjusted_trend():
    """增长客户的 AdjustedTrend_F 必须为正且绝对变化超门槛"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            if row["status"] == "增长":
                assert float(row["adjusted_trend_f"]) > 0
                assert float(row["abs_change"]) > 0

def test_platform_trend_exists():
    """每行都有平台基准趋势"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            assert "platform_trend" in row
            float(row["platform_trend"])  # 不报错即可

def test_reason_tag_not_empty():
    """每个客户都有原因标签"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            assert row["reason_tag"].strip() != ""

def test_suggested_action_not_empty():
    """每个客户都有建议动作"""
    with open(CSV_PATH) as f:
        for row in csv.DictReader(f):
            assert row["suggested_action"].strip() != ""
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_simulate_clients.py -v
```

Expected: FAIL（旧脚本输出不匹配新字段）

**Step 3: 重写 `scripts/simulate_clients.py`**

核心逻辑：

```python
"""
Sales Hub MVP - Mock Client Data Generator (v2)

数据模型以资金沉淀（F）为北极星：
- F_base: 30 天日均资沉 (USDT)
- F_recent: 7 天日均资沉 (USDT)
- Trend_F: (F_recent - F_base) / F_base
- PlatformTrend: 平台整体资沉变化（模拟）
- AdjustedTrend_F: Trend_F - PlatformTrend（剔除市场噪音）
- Status: 增长 / 流失 / 稳定 (基于双门槛: 相对% + 绝对金额)

约束条件来源: MVP 方案补充约束版 §17
"""
import csv, random, math

random.seed(42)
N = 100
OUTPUT = "data/clients_simulation_v2.csv"

# 阈值
T_F_PERCENTILE = 0.80  # 重点客户门槛
DELTA = 0.10            # 相对变化阈值 (10%)
T_DROP = 50000          # 绝对流失门槛 (5 万 USDT)
T_GROWTH = 50000        # 绝对增长门槛 (5 万 USDT)

# 中文姓名池
SURNAMES = ["张", "李", "王", "刘", "陈", "杨", "赵", "黄", "周", "吴",
            "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
GIVEN_NAMES = ["伟", "芳", "娜", "敏", "强", "磊", "洋", "勇", "军", "杰",
               "涛", "明", "超", "秀英", "华", "丽", "静", "建国", "文", "志强"]

# 原因标签池
CHURN_REASONS = ["理财到期/赎回", "近期连续出金", "长时间未登录", "U卡场景绑定弱", "权益不足/续存未触达"]
GROWTH_REASONS = ["近期持续入金", "理财续存", "积分活动参与", "卡场景开始渗透", "平台活跃提升"]
STABLE_REASONS = ["高资沉、稳定沉淀", "资沉高、场景关系浅", "资沉高、近期有增长机会"]

# 动作白名单
CHURN_ACTIONS = ["安排销售回访", "续存提醒+权益说明", "资沉补贴券"]
GROWTH_ACTIONS = ["推荐U卡积分活动", "场景绑定说明", "续存提醒+权益说明"]
STABLE_ACTIONS = ["推荐U卡积分活动", "场景绑定说明", "安排销售回访"]

# 业务线参与概率 (按客户大小分层)
BIZ_LINES = ["futures", "leverage", "savings", "card", "cloud", "mini"]


def generate_name():
    return random.choice(SURNAMES) + random.choice(GIVEN_NAMES)


def generate_uid():
    return str(random.randint(10000000, 99999999))


def lognormal(mu, sigma):
    return math.exp(random.gauss(mu, sigma))


def generate_clients():
    # 模拟平台整体趋势（如近期市场微跌 3%）
    platform_trend = random.uniform(-0.08, 0.05)

    clients = []
    for _ in range(N):
        # F_base: 对数正态分布，中位数约 500 万 USDT
        f_base = lognormal(15.4, 1.8)  # median ~= 5M USDT

        # Trend_F: 大部分稳定，少量增长/流失
        trend_roll = random.random()
        if trend_roll < 0.25:
            # 流失（客户行为 + 市场）
            trend_f = platform_trend + (-random.uniform(0.05, 0.50))
        elif trend_roll < 0.50:
            # 增长（客户行为 + 市场）
            trend_f = platform_trend + random.uniform(0.05, 0.60)
        else:
            # 稳定（主要跟随市场）
            trend_f = platform_trend + random.uniform(-0.04, 0.04)

        f_recent = f_base * (1 + trend_f)
        abs_change = f_recent - f_base
        adjusted_trend_f = trend_f - platform_trend

        # 业务线参与 (资沉越高，参与越多)
        biz = {}
        for line in BIZ_LINES:
            if f_base > 1e7:  # > 1000 万
                biz[line] = random.random() < 0.7
            elif f_base > 1e6:  # > 100 万
                biz[line] = random.random() < 0.4
            else:
                biz[line] = random.random() < 0.15

        clients.append({
            "uid": generate_uid(),
            "name": generate_name(),
            "f_base": f_base,
            "f_recent": f_recent,
            "trend_f": trend_f,
            "platform_trend": platform_trend,
            "adjusted_trend_f": adjusted_trend_f,
            "abs_change": abs_change,
            **{f"has_{line}": biz[line] for line in BIZ_LINES},
        })

    return clients


def classify_and_enrich(clients):
    """分类、排序、补标签和动作（双门槛: 相对% + 绝对金额）"""
    # 计算 T_F 门槛
    sorted_by_f = sorted(clients, key=lambda c: c["f_base"])
    t_f = sorted_by_f[int(len(sorted_by_f) * T_F_PERCENTILE)]["f_base"]

    for c in clients:
        adj = c["adjusted_trend_f"]
        abs_chg = abs(c["abs_change"])

        # 双门槛判定: 相对变化超 δ 且 绝对金额超门槛
        is_churn = (c["f_base"] >= t_f
                    and adj <= -DELTA
                    and abs_chg >= T_DROP)
        is_growth = (c["f_base"] >= t_f
                     and adj >= DELTA
                     and abs_chg >= T_GROWTH)

        # 流失优先于增长（§11: 先止损再增长）
        if is_churn:
            c["status"] = "流失"
            c["churn_priority"] = c["f_base"] * abs(adj)
            c["growth_priority"] = 0
            c["reason_tag"] = random.choice(CHURN_REASONS)
            c["suggested_action"] = random.choice(CHURN_ACTIONS)
        elif is_growth:
            c["status"] = "增长"
            c["churn_priority"] = 0
            c["growth_priority"] = c["f_base"] * adj
            c["reason_tag"] = random.choice(GROWTH_REASONS)
            c["suggested_action"] = random.choice(GROWTH_ACTIONS)
        else:
            c["status"] = "稳定"
            c["churn_priority"] = 0
            c["growth_priority"] = 0
            c["reason_tag"] = random.choice(STABLE_REASONS)
            c["suggested_action"] = random.choice(STABLE_ACTIONS)

    return clients


def write_csv(clients):
    fields = [
        "uid", "name", "f_base", "f_recent",
        "trend_f", "platform_trend", "adjusted_trend_f", "abs_change",
        "status", "churn_priority", "growth_priority",
        "reason_tag", "suggested_action",
        "has_futures", "has_leverage", "has_savings",
        "has_card", "has_cloud", "has_mini",
    ]
    with open(OUTPUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for c in clients:
            row = {}
            for field in fields:
                val = c[field]
                if isinstance(val, float):
                    row[field] = f"{val:.2f}"
                elif isinstance(val, bool):
                    row[field] = "1" if val else "0"
                else:
                    row[field] = val
                row[field] = row[field]
            writer.writerow(row)


if __name__ == "__main__":
    clients = generate_clients()
    clients = classify_and_enrich(clients)
    write_csv(clients)
    # 统计
    churn = sum(1 for c in clients if c["status"] == "流失")
    growth = sum(1 for c in clients if c["status"] == "增长")
    stable = sum(1 for c in clients if c["status"] == "稳定")
    print(f"Generated {N} clients → {OUTPUT}")
    print(f"  流失: {churn}  增长: {growth}  稳定: {stable}")
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_simulate_clients.py -v
```

Expected: ALL PASS

**Step 5: Commit**

```bash
git add scripts/simulate_clients.py tests/test_simulate_clients.py data/
git commit -m "feat: rewrite mock data generator for deposit-centric MVP"
```

---

## Task 3: 重写数据合约 (prototype_data.py)

**Files:**
- Rewrite: `scripts/prototype_data.py`
- Test: `tests/test_prototype_data.py`

**Step 1: 写测试 `tests/test_prototype_data.py`**

```python
import json
import csv
from scripts.prototype_data import build_mock_data

def load_csv():
    with open("data/clients_simulation_v2.csv") as f:
        return list(csv.DictReader(f))

def test_mock_data_structure():
    """数据合约包含必需的顶层字段"""
    rows = load_csv()
    data = build_mock_data(rows)
    assert "generatedAt" in data
    assert "clients" in data
    assert "clientsById" in data
    assert len(data["clients"]) == 100

def test_client_card_fields():
    """每个客户包含卡片所需的四项信息"""
    rows = load_csv()
    data = build_mock_data(rows)
    for c in data["clients"]:
        assert "depositDisplay" in c      # 资沉总量
        assert "status" in c               # 近期状态
        assert "reasonTag" in c            # 原因标签
        assert "suggestedAction" in c      # 建议动作

def test_view_lists():
    """数据包含三视图的 UID 列表"""
    rows = load_csv()
    data = build_mock_data(rows)
    assert "depositRankUids" in data       # 资沉总量（全量按 F_base 降序）
    assert "churnUids" in data             # 资沉流失
    assert "growthUids" in data            # 资沉增长

def test_deposit_rank_sorted():
    """资沉总量视图按 F_base 降序"""
    rows = load_csv()
    data = build_mock_data(rows)
    uids = data["depositRankUids"]
    deposits = [data["clientsById"][uid]["fBase"] for uid in uids]
    assert deposits == sorted(deposits, reverse=True)

def test_churn_sorted():
    """流失视图按 ChurnPriority 降序"""
    rows = load_csv()
    data = build_mock_data(rows)
    uids = data["churnUids"]
    priorities = [data["clientsById"][uid]["churnPriority"] for uid in uids]
    assert priorities == sorted(priorities, reverse=True)

def test_growth_sorted():
    """增长视图按 GrowthPriority 降序"""
    rows = load_csv()
    data = build_mock_data(rows)
    uids = data["growthUids"]
    priorities = [data["clientsById"][uid]["growthPriority"] for uid in uids]
    assert priorities == sorted(priorities, reverse=True)
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_prototype_data.py -v
```

Expected: FAIL

**Step 3: 重写 `scripts/prototype_data.py`**

核心数据合约 `window.PROTOTYPE_DATA`：

```python
"""
Sales Hub MVP - Mock Data Contract Builder (v2)

输出 window.PROTOTYPE_DATA JSON，供所有原型页面消费。
数据结构以资金沉淀三视图为核心。
"""
import json
from datetime import datetime

def _fmt_deposit(val):
    """格式化资沉金额显示"""
    v = float(val)
    if v >= 1e8:
        return f"$ {v/1e8:.1f} 亿"
    elif v >= 1e4:
        return f"$ {v/1e4:.0f} 万"
    else:
        return f"$ {v:.0f}"

def _fmt_trend(trend_f):
    """格式化趋势百分比"""
    v = float(trend_f)
    if v > 0:
        return f"+{v*100:.1f}%"
    else:
        return f"{v*100:.1f}%"

def _status_badge(status):
    """状态对应的颜色 token"""
    return {
        "流失": {"bg": "rgba(246,70,93,0.15)", "text": "#F6465D"},
        "增长": {"bg": "rgba(14,203,129,0.15)", "text": "#0ECB81"},
        "稳定": {"bg": "rgba(132,142,156,0.15)", "text": "#848E9C"},
    }.get(status, {"bg": "#2B3139", "text": "#848E9C"})

def _biz_summary(row):
    """业务线参与概况"""
    lines = []
    mapping = {
        "has_futures": "合约", "has_leverage": "杠杆",
        "has_savings": "理财", "has_card": "金融卡",
        "has_cloud": "云算力", "has_mini": "Mini合约",
    }
    for key, name in mapping.items():
        if row.get(key) == "1":
            lines.append(name)
    return lines

def build_mock_data(rows):
    clients = []
    for row in rows:
        f_base = float(row["f_base"])
        f_recent = float(row["f_recent"])
        trend_f = float(row["trend_f"])
        churn_p = float(row["churn_priority"])
        growth_p = float(row["growth_priority"])
        badge = _status_badge(row["status"])

        clients.append({
            "uid": row["uid"],
            "name": row["name"],
            "fBase": f_base,
            "fRecent": f_recent,
            "trendF": trend_f,
            "platformTrend": float(row["platform_trend"]),
            "adjustedTrendF": float(row["adjusted_trend_f"]),
            "absChange": float(row["abs_change"]),
            "status": row["status"],
            "churnPriority": churn_p,
            "growthPriority": growth_p,
            "reasonTag": row["reason_tag"],
            "suggestedAction": row["suggested_action"],
            # 显示用
            "depositDisplay": _fmt_deposit(f_base),
            "trendDisplay": _fmt_trend(float(row["adjusted_trend_f"])),
            "absChangeDisplay": _fmt_deposit(abs(float(row["abs_change"]))),
            "statusBadge": badge,
            "bizLines": _biz_summary(row),
            "bizCount": len(_biz_summary(row)),
            # 详情页链接
            "detailHref": f"client-detail.html?uid={row['uid']}",
        })

    clients_by_id = {c["uid"]: c for c in clients}

    # 三视图排序
    deposit_rank = sorted(clients, key=lambda c: c["fBase"], reverse=True)
    churn_list = sorted(
        [c for c in clients if c["status"] == "流失"],
        key=lambda c: c["churnPriority"], reverse=True
    )
    growth_list = sorted(
        [c for c in clients if c["status"] == "增长"],
        key=lambda c: c["growthPriority"], reverse=True
    )

    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d"),
        "clients": clients,
        "clientsById": clients_by_id,
        "depositRankUids": [c["uid"] for c in deposit_rank],
        "churnUids": [c["uid"] for c in churn_list],
        "growthUids": [c["uid"] for c in growth_list],
    }

def to_js(data):
    """输出为 window.PROTOTYPE_DATA = {...}; 格式"""
    return f"window.PROTOTYPE_DATA = {json.dumps(data, ensure_ascii=False)};"
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_prototype_data.py -v
```

Expected: ALL PASS

**Step 5: Commit**

```bash
git add scripts/prototype_data.py tests/test_prototype_data.py
git commit -m "feat: rewrite data contract for deposit-centric three-view model"
```

---

## Task 4: 重写首页原型 (三视图 Tab)

**Files:**
- Create: `prototype/home.html` (新首页，替代 home-a/b/c)
- Modify: `prototype/index.html` (入口直接跳转 home.html)
- Archive: `prototype/home-a.html`, `prototype/home-b.html`, `prototype/home-c.html` → 不删除但不再链入

**Step 1: 写首页 `prototype/home.html`**

页面结构：

```
┌─────────────────────────┐
│ Status Bar (44px)        │
├─────────────────────────┤
│ Top Nav: "销售工作台"     │
├─────────────────────────┤
│ ┌───────┬──────┬──────┐ │
│ │ 总量  │ 流失 │ 增长 │ │ ← 三个 Tab
│ └───────┴──────┴──────┘ │
├─────────────────────────┤
│ Client Card 1            │
│ ┌─────────────────────┐ │
│ │ 张伟          $850万 │ │
│ │ ● 稳定               │ │
│ │ 高资沉、场景关系浅   │ │
│ │ → 推荐U卡积分活动    │ │
│ └─────────────────────┘ │
│ Client Card 2            │
│ ...                      │
├─────────────────────────┤
│ Bottom Tab Bar (56px)    │
└─────────────────────────┘
```

关键实现细节：

- **Tab 切换**: JS 切换数据源（depositRankUids / churnUids / growthUids）
- **卡片渲染**: 统一 `renderCard(client)` 函数
- **流失 Tab**: 红色调，排序 = ChurnPriority
- **增长 Tab**: 绿色调，排序 = GrowthPriority
- **总量 Tab**: 中性色，排序 = F_base
- **流失 Tab 客户数量 badge**: Tab 上显示数字提醒

CSS 沿用现有设计系统：
- 背景: `#0B0E11` / `#1E2329`
- 金色强调: `#F0B90B`
- 流失红: `#F6465D`
- 增长绿: `#0ECB81`
- 卡片: 12px radius, `#1E2329` bg

**Step 2: 更新入口 `prototype/index.html`**

将版本选择页改为直接跳转:

```html
<meta http-equiv="refresh" content="0;url=home.html">
```

或保留为简单的跳转页。

**Step 3: 更新底部导航**

Bottom Tab Bar 保持 4 个 Tab:
- 首页 (home.html) ← active
- 客户 (clients.html)
- 事件 (events.html)
- 我的 (profile.html)

**Step 4: 在浏览器中打开验证**

```bash
open prototype/home.html
```

验证：
- [ ] 三个 Tab 可切换
- [ ] 总量 Tab 按资沉降序
- [ ] 流失 Tab 只显示流失客户，红色调
- [ ] 增长 Tab 只显示增长客户，绿色调
- [ ] 卡片显示四项信息
- [ ] 点击卡片可跳转 client-detail.html

**Step 5: Commit**

```bash
git add prototype/home.html prototype/index.html
git commit -m "feat: new homepage with deposit/churn/growth three-tab view"
```

---

## Task 5: 重写客户卡片组件

**Files:**
- Embedded in: `prototype/home.html` (已在 Task 4 中)
- Also used in: `prototype/clients.html`

**Step 1: 定义卡片 HTML 模板**

每张卡片的 HTML 结构（在 JS 中作为 template literal）：

```html
<div class="bg-[#1E2329] rounded-xl p-4 mb-3 border border-[#2E3440]"
     onclick="location.href='client-detail.html?uid=${c.uid}'">
  <!-- Row 1: 名字 + 资沉 -->
  <div class="flex justify-between items-center mb-2">
    <span class="text-[#EAECEF] font-medium">${c.name}</span>
    <span class="text-[#EAECEF] text-lg font-bold">${c.depositDisplay}</span>
  </div>
  <!-- Row 2: 状态 badge + 趋势 -->
  <div class="flex items-center gap-2 mb-2">
    <span class="text-xs px-2 py-0.5 rounded-full"
          style="background:${c.statusBadge.bg};color:${c.statusBadge.text}">
      ${c.status}
    </span>
    <span class="text-xs" style="color:${c.adjustedTrendF > 0 ? '#0ECB81' : c.adjustedTrendF < 0 ? '#F6465D' : '#848E9C'}">
      ${c.trendDisplay}
    </span>
  </div>
  <!-- Row 3: 原因标签 -->
  <div class="text-xs text-[#848E9C] mb-1">${c.reasonTag}</div>
  <!-- Row 4: 建议动作 -->
  <div class="text-xs text-[#F0B90B]">→ ${c.suggestedAction}</div>
</div>
```

**Step 2: 更新 `prototype/clients.html`**

客户列表页也需要用新卡片格式。原来的列表是按 N90 排的，现在改为按 F_base 排。

搜索/筛选功能保留：按名字搜索、按状态筛选（全部/流失/增长/稳定）。

**Step 3: 验证**

```bash
open prototype/clients.html
```

验证：
- [ ] 列表按资沉降序
- [ ] 卡片显示新格式
- [ ] 搜索正常
- [ ] 状态筛选正常

**Step 4: Commit**

```bash
git add prototype/clients.html
git commit -m "feat: update clients list with deposit-centric card format"
```

---

## Task 6: 重写客户详情页

**Files:**
- Rewrite: `prototype/client-detail.html`

**Step 1: 重新设计详情页结构**

新结构（以资沉为核心）：

```
┌─────────────────────────┐
│ ← 返回    客户详情       │
├─────────────────────────┤
│ 张伟                     │
│ UID: 41329612            │
│ ● 流失                   │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ 当前资沉             │ │
│ │ $ 1,200 万           │ │
│ │ 30日均 ▼ 7日均      │ │
│ │ $1,350万   $1,200万  │ │
│ │ Trend: -11.1%        │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ 原因分析                 │
│ 理财到期/赎回            │
├─────────────────────────┤
│ 建议动作                 │
│ → 安排销售回访 +         │
│   续存权益说明            │
├─────────────────────────┤
│ 业务参与情况              │
│ ✓ 合约  ✓ 理财  ✗ U卡   │
│ ✓ 杠杆  ✗ 云算力 ✗ Mini │
├─────────────────────────┤
│ BD 备注                   │
│ [可编辑文本区域]          │
├─────────────────────────┤
│ 跟进记录                  │
│ 03-28 14:30 已电话回访    │
│ 03-25 10:00 发送续存提醒  │
└─────────────────────────┘
```

核心变化：
- 移除 N90, E90 作为头部指标
- 资沉总量（F_base）成为最大数字
- 显示 F_base vs F_recent 对比
- 显示 Trend_F 百分比
- 业务参与情况简化为 ✓/✗ 列表
- 移除复杂的机会缺口分析
- 保留 BD 备注和跟进记录

**Step 2: 实现页面**

从 `window.PROTOTYPE_DATA.clientsById[uid]` 读取数据渲染。

**Step 3: 验证**

```bash
open "prototype/client-detail.html?uid=41329612"
```

验证：
- [ ] 资沉总量显示正确
- [ ] 趋势百分比显示正确
- [ ] 状态 badge 颜色正确
- [ ] 业务参与列表正确
- [ ] 返回按钮正常

**Step 4: Commit**

```bash
git add prototype/client-detail.html
git commit -m "feat: redesign client detail page around deposit metrics"
```

---

## Task 7: 更新数据生成管线

**Files:**
- Rewrite: `scripts/generate_prototype.py`

**Step 1: 重写 `scripts/generate_prototype.py`**

简化为：
1. 读取 `data/clients_simulation_v2.csv`
2. 调用 `prototype_data.build_mock_data()` 构建 JSON
3. 输出 `prototype/mock-data.js`

不再生成多个 HTML 版本（home-a/b/c 已废弃）。

```python
"""
Sales Hub MVP - Prototype Data Injector (v2)

读取 CSV → 构建 JSON → 输出 mock-data.js
"""
import csv
from scripts.prototype_data import build_mock_data, to_js

CSV_PATH = "data/clients_simulation_v2.csv"
OUTPUT = "prototype/mock-data.js"

def main():
    with open(CSV_PATH) as f:
        rows = list(csv.DictReader(f))

    data = build_mock_data(rows)
    js = to_js(data)

    with open(OUTPUT, "w") as f:
        f.write(js)

    print(f"Generated {OUTPUT}")
    print(f"  Clients: {len(data['clients'])}")
    print(f"  Churn: {len(data['churnUids'])}")
    print(f"  Growth: {len(data['growthUids'])}")

if __name__ == "__main__":
    main()
```

**Step 2: 运行完整管线**

```bash
python3 scripts/simulate_clients.py && python3 scripts/generate_prototype.py
```

**Step 3: 在浏览器中端到端验证**

```bash
open prototype/home.html
```

验证：
- [ ] 数据加载正常
- [ ] 三个 Tab 数据正确
- [ ] 点击卡片跳转详情页正常
- [ ] 详情页数据渲染正确

**Step 4: Commit**

```bash
git add scripts/generate_prototype.py prototype/mock-data.js
git commit -m "feat: simplify data pipeline for deposit-centric MVP"
```

---

## Task 8: 简化事件系统（对齐新框架）

**Files:**
- Modify: `prototype/events.html`
- Modify: `prototype/event-thread.html`
- Modify: `scripts/prototype_data.py` (补事件数据)

**Step 1: 事件类型对齐新框架**

旧事件类型是围绕"高价值/高潜"设计的。新框架下事件应围绕资沉变化：

| 旧事件类型 | 新事件类型 |
|-----------|-----------|
| 出金预警 | **资沉流失预警**（保留，核心） |
| 充值 | **资沉增长通知**（保留，核心） |
| 爆仓 | 保留（影响资沉） |
| 盈利 | 简化为增长信号 |
| 理财到期 | **理财到期提醒**（新增，直接关联流失风险） |
| 人工 | 保留 |

**Step 2: 在 `prototype_data.py` 中补事件生成逻辑**

为流失和增长客户各生成 2-3 个事件。事件模板精简为 6 种。

**Step 3: 更新 events.html 和 event-thread.html**

事件列表页增加按"流失相关 / 增长相关"的筛选。
事件线程页保留 4 状态（未开始 / 跟进中 / 已完成 / 已忽略）。

**Step 4: 验证**

```bash
open prototype/events.html
```

**Step 5: Commit**

```bash
git add prototype/events.html prototype/event-thread.html scripts/prototype_data.py
git commit -m "feat: align event system with deposit-centric framework"
```

---

## Task 9: 更新 README 和清理

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Clean: 旧文档引用

**Step 1: 重写 README.md**

更新内容：
- 项目描述改为"以资金沉淀为北极星的销售工作台"
- Fact Sources 更新引用
- Data Pipeline 更新命令
- 移除 home-a/b/c 的引用
- 更新 Known Gaps

**Step 2: 更新 AGENTS.md**

更新 coordination root 和当前执行计划引用。

**Step 3: 运行完整管线确认一切正常**

```bash
python3 scripts/simulate_clients.py && python3 scripts/generate_prototype.py && open prototype/home.html
```

**Step 4: 运行所有测试**

```bash
pytest tests/ -v
```

Expected: ALL PASS

**Step 5: Final Commit**

```bash
git add README.md AGENTS.md
git commit -m "docs: update README and AGENTS for deposit-centric MVP"
```

---

## 完成检查清单

### 功能检查
- [ ] 旧文档已归档到 `docs/archive/`
- [ ] 新产品文档 `docs/product-concept-v2.md` 已创建
- [ ] `simulate_clients.py` 输出 v2 CSV（F_base / AdjustedTrend_F / 双门槛 / status）
- [ ] `prototype_data.py` 输出三视图数据合约
- [ ] `generate_prototype.py` 简化为单一管线
- [ ] 首页 `home.html` 三 Tab 视图正常
- [ ] 客户卡片四项信息（资沉、状态、原因、动作）
- [ ] 客户详情页以资沉为核心
- [ ] 客户列表页使用新卡片格式
- [ ] 事件系统对齐资沉框架
- [ ] 所有测试通过
- [ ] README 更新

### 约束条件检查（来自补充约束版 §17）
- [ ] 资沉统一 USDT 计价
- [ ] 取数时点统一 UTC 00:00（文档中明确）
- [ ] 流失/增长采用双门槛（相对% + 绝对金额）
- [ ] 平台基准修正已纳入（AdjustedTrend_F）
- [ ] 动作冷却规则已在数据模型中预留
- [ ] 动作互斥规则已在数据模型中预留
- [ ] 动作留痕字段已定义
