"""
Sales Hub MVP - Mock Data Contract Builder (v2)

输出 window.PROTOTYPE_DATA JSON，供所有原型页面消费。
数据结构以资金沉淀三视图为核心。
"""
import json
from datetime import datetime


def _fmt_deposit(val: float) -> str:
    """格式化资沉金额显示。"""
    if val >= 1e8:
        return f"$ {val / 1e8:.1f} 亿"
    elif val >= 1e4:
        return f"$ {val / 1e4:.0f} 万"
    else:
        return f"$ {val:.0f}"


def _fmt_trend(trend: float) -> str:
    """格式化趋势百分比。"""
    if trend > 0:
        return f"+{trend * 100:.1f}%"
    return f"{trend * 100:.1f}%"


def _status_badge(status: str) -> dict:
    """状态对应的颜色 token。"""
    return {
        "流失": {"bg": "rgba(246,70,93,0.15)", "text": "#F6465D"},
        "增长": {"bg": "rgba(14,203,129,0.15)", "text": "#0ECB81"},
        "稳定": {"bg": "rgba(132,142,156,0.15)", "text": "#848E9C"},
    }.get(status, {"bg": "#2B3139", "text": "#848E9C"})


_BIZ_MAP = {
    "has_futures": "合约",
    "has_leverage": "杠杆",
    "has_savings": "理财",
    "has_card": "金融卡",
    "has_cloud": "云算力",
    "has_mini": "Mini合约",
}


def _biz_summary(row: dict) -> list[str]:
    """业务线参与概况。"""
    return [name for key, name in _BIZ_MAP.items() if row.get(key) == "1"]


def build_mock_data(rows: list[dict]) -> dict:
    """从 CSV 行构建前端数据合约。"""
    clients = []
    for row in rows:
        f_base = float(row["f_base"])
        f_recent = float(row["f_recent"])
        adj_trend = float(row["adjusted_trend_f"])
        abs_chg = float(row["abs_change"])
        churn_p = float(row["churn_priority"])
        growth_p = float(row["growth_priority"])
        badge = _status_badge(row["status"])
        biz = _biz_summary(row)

        clients.append({
            "uid": row["uid"],
            "name": row["name"],
            # 核心数据
            "fBase": f_base,
            "fRecent": f_recent,
            "trendF": float(row["trend_f"]),
            "platformTrend": float(row["platform_trend"]),
            "adjustedTrendF": adj_trend,
            "absChange": abs_chg,
            # 分类
            "status": row["status"],
            "churnPriority": churn_p,
            "growthPriority": growth_p,
            # 标签和动作
            "reasonTag": row["reason_tag"],
            "suggestedAction": row["suggested_action"],
            # 显示用
            "depositDisplay": _fmt_deposit(f_base),
            "trendDisplay": _fmt_trend(adj_trend),
            "absChangeDisplay": _fmt_deposit(abs(abs_chg)),
            "statusBadge": badge,
            "bizLines": biz,
            "bizCount": len(biz),
            # 导航
            "detailHref": f"client-detail.html?uid={row['uid']}",
        })

    by_id = {c["uid"]: c for c in clients}

    # 三视图排序
    deposit_rank = sorted(clients, key=lambda c: c["fBase"], reverse=True)
    churn_list = sorted(
        [c for c in clients if c["status"] == "流失"],
        key=lambda c: c["churnPriority"],
        reverse=True,
    )
    growth_list = sorted(
        [c for c in clients if c["status"] == "增长"],
        key=lambda c: c["growthPriority"],
        reverse=True,
    )

    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d"),
        "platformTrend": float(rows[0]["platform_trend"]) if rows else 0,
        "platformTrendDisplay": _fmt_trend(float(rows[0]["platform_trend"])) if rows else "0%",
        "clients": clients,
        "clientsById": by_id,
        "depositRankUids": [c["uid"] for c in deposit_rank],
        "churnUids": [c["uid"] for c in churn_list],
        "growthUids": [c["uid"] for c in growth_list],
        "stats": {
            "total": len(clients),
            "churn": len(churn_list),
            "growth": len(growth_list),
            "stable": len(clients) - len(churn_list) - len(growth_list),
        },
    }


def to_js(data: dict) -> str:
    """输出为 window.PROTOTYPE_DATA = {...}; 格式。"""
    return f"window.PROTOTYPE_DATA = {json.dumps(data, ensure_ascii=False)};"
