"""
Sales Hub MVP - Mock Data Contract Builder (v3)

8-week regression model. Source: docs/product-concept-v2.md
"""
import json
from datetime import datetime


def _fmt_deposit(val):
    if val >= 1e8:
        return f"$ {val/1e8:.1f} 亿"
    elif val >= 1e4:
        return f"$ {val/1e4:.0f} 万"
    else:
        return f"$ {val:.0f}"


def _fmt_trend_rate(rate):
    """Format as %/week."""
    if rate > 0:
        return f"+{rate*100:.1f}%/周"
    return f"{rate*100:.1f}%/周"


def _status_badge(status):
    return {
        "流失": {"bg": "rgba(246,70,93,0.15)", "text": "#F6465D"},
        "增长": {"bg": "rgba(14,203,129,0.15)", "text": "#0ECB81"},
        "稳定": {"bg": "rgba(132,142,156,0.15)", "text": "#848E9C"},
    }.get(status, {"bg": "#2B3139", "text": "#848E9C"})


def _trend_confidence_label(r2):
    if r2 >= 0.7:
        return "趋势明确"
    return "波动较大"


_BIZ_MAP = {
    "has_futures": "合约", "has_leverage": "杠杆",
    "has_savings": "理财", "has_card": "金融卡",
    "has_cloud": "云算力", "has_mini": "Mini合约",
}


def _biz_summary(row):
    return [name for key, name in _BIZ_MAP.items() if row.get(key) == "1"]


def build_mock_data(rows):
    clients = []
    for row in rows:
        f_mean = float(row["f_mean"])
        adj_rate = float(row["adjusted_trend_rate"])
        r2 = float(row["r_squared"])
        conf = float(row["conf"])
        churn_s = float(row["churn_score"])
        growth_s = float(row["growth_score"])
        badge = _status_badge(row["status"])
        biz = _biz_summary(row)

        # Weekly values for detail page
        weeks = [float(row[f"w{i}"]) for i in range(1, 9)]

        clients.append({
            "uid": row["uid"],
            "name": row["name"],
            # Core
            "fMean": f_mean,
            "weeks": weeks,
            "trendRate": float(row["trend_rate"]),
            "adjustedTrendRate": adj_rate,
            "rSquared": r2,
            "conf": conf,
            "platformTrendRate": float(row["platform_trend_rate"]),
            # Scores
            "churnScore": churn_s,
            "growthScore": growth_s,
            "status": row["status"],
            # Labels
            "reasonTag": row["reason_tag"],
            "suggestedAction": row["suggested_action"],
            # Display
            "depositDisplay": _fmt_deposit(f_mean),
            "thisWeekDisplay": _fmt_deposit(weeks[-1]),
            "trendDisplay": _fmt_trend_rate(adj_rate),
            "trendConfidence": _trend_confidence_label(r2),
            "statusBadge": badge,
            "bizLines": biz,
            "bizCount": len(biz),
            "detailHref": f"client-detail.html?uid={row['uid']}",
        })

    by_id = {c["uid"]: c for c in clients}

    # Three views
    deposit_rank = sorted(clients, key=lambda c: c["fMean"], reverse=True)
    churn_list = sorted(
        [c for c in clients if c["churnScore"] > 0],
        key=lambda c: c["churnScore"], reverse=True,
    )
    growth_list = sorted(
        [c for c in clients if c["growthScore"] > 0],
        key=lambda c: c["growthScore"], reverse=True,
    )

    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d"),
        "platformTrendRate": float(rows[0]["platform_trend_rate"]) if rows else 0,
        "platformTrendDisplay": _fmt_trend_rate(float(rows[0]["platform_trend_rate"])) if rows else "0%/周",
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


def to_js(data):
    return f"window.PROTOTYPE_DATA = {json.dumps(data, ensure_ascii=False)};"
