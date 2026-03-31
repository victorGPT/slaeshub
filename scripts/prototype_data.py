"""
Sales Hub MVP - Mock Data Contract Builder (v4)

8-week regression model + deposit distribution, net contribution,
client P&L, events, and welfare fund.
Source: docs/product-concept-v2.md
"""
import json
import random
from datetime import datetime

random.seed(99)


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


def _fmt_pnl(val):
    """Format P&L with sign and color."""
    sign = "+" if val > 0 else ""
    if abs(val) >= 1e4:
        display = f"{sign}{val/1e4:.1f}万"
    else:
        display = f"{sign}{val:.0f}"
    color = "#0ECB81" if val > 0 else "#F6465D" if val < 0 else "#848E9C"
    return {"value": val, "display": display, "color": color}


def _fmt_pct(val):
    """Format a ratio as percentage with sign."""
    sign = "+" if val > 0 else ""
    return f"{sign}{val*100:.1f}%"


EVENT_TEMPLATES = {
    'large_withdraw': {
        'type': '大额出金', 'urgency': 'critical', 'color': '#F6465D',
        'action': '立即联系，了解出金原因',
        'script': '张总您好，注意到您最近有一笔资金调整，想跟您确认一下是否有什么我们可以协助的地方？',
    },
    'risk_control': {
        'type': '风控触发', 'urgency': 'critical', 'color': '#F6465D',
        'action': '一键复制客户信息，发给研发排查',
        'script': None,
        'copy_template': '客户 UID: {uid}\n风控类型: {risk_type}\n触发时间: {time}\n客户资沉: {deposit}\n请协助排查，谢谢。',
    },
    'large_loss': {
        'type': '大额亏损', 'urgency': 'warning', 'color': '#F0A030',
        'action': '关怀客户情绪，建议风控',
        'script': '注意到您最近的交易有些波动，如果需要任何帮助或想了解风控方案，随时联系我。',
    },
    'finance_expiry': {
        'type': '理财到期', 'urgency': 'warning', 'color': '#F0B90B',
        'action': '提醒续存，推送权益说明',
        'script': '您好，您的理财产品即将到期，目前有续存权益方案，年化可以到 X%，需要我帮您了解一下吗？',
    },
    'large_deposit': {
        'type': '大额入金', 'urgency': 'info', 'color': '#0ECB81',
        'action': '感谢并推荐产品',
        'script': '感谢您的信任，您最近入金的资金是否需要配置理财或其他产品？我可以给您推荐适合的方案。',
    },
    'large_profit': {
        'type': '大额盈利', 'urgency': 'info', 'color': '#0ECB81',
        'action': '祝贺并建议锁定部分盈利',
        'script': '恭喜最近收益不错！建议将部分盈利转入理财锁定，我可以帮您看看适合的产品。',
    },
}

_URGENCY_ORDER = {'critical': 0, 'warning': 1, 'info': 2}


def _fmt_amount(val):
    abs_val = abs(val)
    sign = '+' if val > 0 else '-' if val < 0 else ''
    if abs_val >= 1e4:
        return f'{sign}${abs_val/1e4:.0f}万'
    return f'{sign}${abs_val:.0f}'


def _generate_events(uid, name, status, f_mean):
    """Generate 1-3 events per client based on status."""
    events = []

    if status == '流失':
        evt = dict(EVENT_TEMPLATES['large_withdraw'])
        evt['id'] = f'evt-{uid}-001'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['amount'] = -abs(random.uniform(50000, 500000))
        evt['amount_display'] = _fmt_amount(evt['amount'])
        evt['time_ago'] = random.choice(['2小时前', '5小时前', '1天前'])
        evt['task_state'] = random.choice(['待处理', '跟进中'])
        evt['sub_type'] = ''
        events.append(evt)

        if random.random() < 0.4:
            evt2 = dict(EVENT_TEMPLATES['finance_expiry'])
            evt2['id'] = f'evt-{uid}-002'
            evt2['client_uid'] = uid
            evt2['client_name'] = name
            evt2['amount'] = random.uniform(100000, 2000000)
            evt2['amount_display'] = _fmt_amount(evt2['amount'])
            evt2['time_ago'] = random.choice(['今天', '明天', '3天后'])
            evt2['task_state'] = '待处理'
            evt2['sub_type'] = ''
            events.append(evt2)

    elif status == '增长':
        evt = dict(EVENT_TEMPLATES['large_deposit'])
        evt['id'] = f'evt-{uid}-001'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['amount'] = abs(random.uniform(50000, 800000))
        evt['amount_display'] = _fmt_amount(evt['amount'])
        evt['time_ago'] = random.choice(['1小时前', '3小时前', '昨天'])
        evt['task_state'] = random.choice(['待处理', '已完成'])
        evt['sub_type'] = ''
        events.append(evt)

    else:  # 稳定
        if random.random() < 0.3:
            evt = dict(EVENT_TEMPLATES['finance_expiry'])
            evt['id'] = f'evt-{uid}-001'
            evt['client_uid'] = uid
            evt['client_name'] = name
            evt['amount'] = random.uniform(50000, 500000)
            evt['amount_display'] = _fmt_amount(evt['amount'])
            evt['time_ago'] = random.choice(['3天后', '5天后', '下周'])
            evt['task_state'] = '待处理'
            evt['sub_type'] = ''
            events.append(evt)

    # Random chance of risk control event
    if random.random() < 0.05:
        risk_types = ['提现限制', '交易限制', '账户冻结']
        evt = dict(EVENT_TEMPLATES['risk_control'])
        evt['id'] = f'evt-{uid}-risk'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['risk_type'] = random.choice(risk_types)
        evt['amount'] = 0
        evt['amount_display'] = ''
        evt['time_ago'] = random.choice(['1小时前', '30分钟前'])
        evt['task_state'] = '待处理'
        evt['sub_type'] = evt['risk_type']
        events.append(evt)

    return events


def build_mock_data(rows):
    clients = []
    all_events = []

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

        # Deposit distribution
        deposit_dist = {
            "savings": float(row["dd_savings"]),
            "futuresMargin": float(row["dd_futures_margin"]),
            "spotWallet": float(row["dd_spot_wallet"]),
            "card": float(row["dd_card"]),
            "cloud": float(row["dd_cloud"]),
        }
        deposit_dist["savingsDisplay"] = _fmt_deposit(deposit_dist["savings"])
        deposit_dist["futuresMarginDisplay"] = _fmt_deposit(deposit_dist["futuresMargin"])
        deposit_dist["spotWalletDisplay"] = _fmt_deposit(deposit_dist["spotWallet"])
        deposit_dist["cardDisplay"] = _fmt_deposit(deposit_dist["card"])
        deposit_dist["cloudDisplay"] = _fmt_deposit(deposit_dist["cloud"])

        # Net contribution
        nc_total = float(row["nc_total"])
        nc_wow = float(row["nc_wow"])
        net_contribution = {
            "total": nc_total,
            "totalDisplay": _fmt_deposit(nc_total),
            "futures": float(row["nc_futures"]),
            "leverage": float(row["nc_leverage"]),
            "mini": float(row["nc_mini"]),
            "card": float(row["nc_card"]),
            "cloud": float(row["nc_cloud"]),
            "savingsInterest": float(row["nc_savings_interest"]),
            "rebate": float(row["nc_rebate"]),
            "wow": nc_wow,
            "wowDisplay": _fmt_pct(nc_wow),
        }

        # Client P&L
        pnl_7d = float(row["pnl_7d_total"])
        pnl_8w = float(row["pnl_8w_weekly_avg"])
        client_pnl = {
            "total7d": _fmt_pnl(pnl_7d),
            "futures7d": _fmt_pnl(float(row["pnl_7d_futures"])),
            "leverage7d": _fmt_pnl(float(row["pnl_7d_leverage"])),
            "mini7d": _fmt_pnl(float(row["pnl_7d_mini"])),
            "spot7d": _fmt_pnl(float(row["pnl_7d_spot"])),
            "weeklyAvg8w": _fmt_pnl(pnl_8w),
        }

        # Welfare fund
        welfare = {
            "budget": float(row["welfare_budget"]),
            "sent": float(row["welfare_sent"]),
            "activated": float(row["welfare_activated"]),
            "remaining": float(row["welfare_remaining"]),
            "budgetDisplay": _fmt_deposit(float(row["welfare_budget"])),
            "sentDisplay": _fmt_deposit(float(row["welfare_sent"])),
            "activatedDisplay": _fmt_deposit(float(row["welfare_activated"])),
            "remainingDisplay": _fmt_deposit(float(row["welfare_remaining"])),
        }

        # Events
        uid = row["uid"]
        name = row["name"]
        client_events = _generate_events(uid, name, row["status"], f_mean)
        all_events.extend(client_events)

        clients.append({
            "uid": uid,
            "name": name,
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
            "detailHref": f"client-detail.html?uid={uid}",
            # New fields
            "depositDist": deposit_dist,
            "netContribution": net_contribution,
            "clientPnl": client_pnl,
            "welfare": welfare,
            "events": client_events,
        })

    by_id = {c["uid"]: c for c in clients}

    # Sort events by urgency then time
    all_events.sort(key=lambda e: _URGENCY_ORDER.get(e.get("urgency", "info"), 9))

    # Events by client UID lookup
    events_by_uid = {}
    for evt in all_events:
        cuid = evt["client_uid"]
        events_by_uid.setdefault(cuid, []).append(evt)

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
        "events": all_events,
        "eventsByClientUid": events_by_uid,
        "stats": {
            "total": len(clients),
            "churn": len(churn_list),
            "growth": len(growth_list),
            "stable": len(clients) - len(churn_list) - len(growth_list),
            "eventCount": len(all_events),
            "criticalEvents": sum(1 for e in all_events if e.get("urgency") == "critical"),
        },
    }


def to_js(data):
    return f"window.PROTOTYPE_DATA = {json.dumps(data, ensure_ascii=False)};"
