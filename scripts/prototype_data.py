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
    'risk_control': {
        'type': '风控触发', 'urgency': 'critical', 'color': '#F6465D',
        'action': '一键复制客户信息，发给研发排查',
        'script': None,
        'copy_template': '客户 UID: {uid}\n风控类型: {risk_type}\n触发时间: {time}\n客户资沉: {deposit}\n请协助排查，谢谢。',
    },
    'mega_withdraw': {
        'type': '超大额出金', 'urgency': 'critical', 'color': '#F6465D',
        'action': '挽留话术 + 福利金',
        'script': '张总您好，注意到您最近有一笔较大的资金调整，想跟您确认一下是否有什么我们可以协助的地方？',
    },
    'liquidation': {
        'type': '爆仓', 'urgency': 'critical', 'color': '#F6465D',
        'action': '安抚话术 + 风控教育',
        'script': '注意到您最近的仓位有波动，我们有一些风控工具可以帮助管理风险，方便的话我给您介绍一下？',
    },
}

_URGENCY_ORDER = {'critical': 0, 'warning': 1, 'info': 2}


def _fmt_amount(val):
    abs_val = abs(val)
    sign = '+' if val > 0 else '-' if val < 0 else ''
    if abs_val >= 1e4:
        return f'{sign}${abs_val/1e4:.0f}万'
    return f'{sign}${abs_val:.0f}'


def _generate_events_and_activities(uid, name, status, f_mean, row):
    """Generate events (push to homepage) and activities (client detail only).

    Events (3 types): 风控触发, 超大额出金, 爆仓
    Activities (5 types): 大额出金, 大额入金, 理财到期, 大额盈利, 大额亏损
    """
    events = []
    activities = []
    evt_counter = 0
    act_counter = 0

    has_futures = row.get('has_futures') == '1'
    has_leverage = row.get('has_leverage') == '1'
    has_savings = row.get('has_savings') == '1'
    has_trading = has_futures or has_leverage or row.get('has_mini') == '1'

    # Time choices with numeric age_hours for auto-expiry
    _RECENT_TIMES = [
        ('30分钟前', 0.5), ('1小时前', 1), ('2小时前', 2),
        ('3小时前', 3), ('5小时前', 5), ('6小时前', 6),
    ]
    _MEDIUM_TIMES = [
        ('1天前', 24), ('2天前', 48), ('昨天', 20),
    ]
    _OLD_TIMES = [
        ('3天前', 72), ('4天前', 96), ('5天前', 120),
    ]

    def _pick_time(choices):
        t = random.choice(choices)
        return t[0], t[1]

    # --- Events (push to homepage, need action) ---

    # 1. 风控触发: 流失客户 30% 概率
    if status == '流失' and random.random() < 0.3:
        evt_counter += 1
        risk_types = ['提现限制', '交易限制', '账户冻结', 'KYC异常']
        risk_type = random.choice(risk_types)
        time_ago, age_hours = _pick_time(_RECENT_TIMES + _MEDIUM_TIMES)
        evt = dict(EVENT_TEMPLATES['risk_control'])
        evt['id'] = f'evt-{uid}-{evt_counter:03d}'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['risk_type'] = risk_type
        evt['amount'] = 0
        evt['amount_display'] = ''
        evt['time_ago'] = time_ago
        evt['age_hours'] = age_hours
        evt['task_state'] = '待处理'
        evt['sub_type'] = risk_type
        evt['expires_in'] = None  # 风控不过期
        events.append(evt)

    # 2. 超大额出金: 流失客户 40% 概率, 金额 >= fMean * 30%
    if status == '流失' and random.random() < 0.4:
        evt_counter += 1
        amount = -abs(f_mean * random.uniform(0.3, 0.6))
        time_ago, age_hours = _pick_time(_RECENT_TIMES + _MEDIUM_TIMES + _OLD_TIMES)
        evt = dict(EVENT_TEMPLATES['mega_withdraw'])
        evt['id'] = f'evt-{uid}-{evt_counter:03d}'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['amount'] = amount
        evt['amount_display'] = _fmt_amount(amount)
        evt['time_ago'] = time_ago
        evt['age_hours'] = age_hours
        # 超过48小时自动过期
        evt['task_state'] = '已过期' if age_hours > 48 else random.choice(['待处理', '跟进中'])
        evt['sub_type'] = ''
        evt['expires_in'] = '48小时'
        events.append(evt)

    # 3. 爆仓: 有合约或杠杆的客户 20% 概率
    if (has_futures or has_leverage) and random.random() < 0.2:
        evt_counter += 1
        sub = random.choice(
            (['合约爆仓'] if has_futures else [])
            + (['杠杆爆仓'] if has_leverage else [])
        )
        time_ago, age_hours = _pick_time(_RECENT_TIMES + _MEDIUM_TIMES + _OLD_TIMES)
        evt = dict(EVENT_TEMPLATES['liquidation'])
        evt['id'] = f'evt-{uid}-{evt_counter:03d}'
        evt['client_uid'] = uid
        evt['client_name'] = name
        evt['amount'] = -abs(f_mean * random.uniform(0.05, 0.2))
        evt['amount_display'] = _fmt_amount(evt['amount'])
        evt['time_ago'] = time_ago
        evt['age_hours'] = age_hours
        # 超过72小时自动过期
        evt['task_state'] = '已过期' if age_hours > 72 else '待处理'
        evt['sub_type'] = sub
        evt['expires_in'] = '72小时'
        events.append(evt)

    # --- Activities (client detail timeline only) ---

    # 普通大额出金 (< 30% 资沉): 流失客户 60% 概率
    if status == '流失' and random.random() < 0.6:
        act_counter += 1
        amount = -abs(f_mean * random.uniform(0.05, 0.29))
        activities.append({
            'id': f'act-{uid}-{act_counter:03d}',
            'client_uid': uid,
            'client_name': name,
            'type': '大额出金',
            'sub_type': '',
            'amount_display': _fmt_amount(amount),
            'time_ago': random.choice(['2小时前', '5小时前', '1天前', '2天前']),
        })

    # 大额入金: 增长/稳定客户 50% 概率
    if status in ('增长', '稳定') and random.random() < 0.5:
        act_counter += 1
        amount = abs(f_mean * random.uniform(0.05, 0.3))
        activities.append({
            'id': f'act-{uid}-{act_counter:03d}',
            'client_uid': uid,
            'client_name': name,
            'type': '大额入金',
            'sub_type': '',
            'amount_display': _fmt_amount(amount),
            'time_ago': random.choice(['1小时前', '3小时前', '昨天']),
        })

    # 理财到期: 有理财业务 40% 概率
    if has_savings and random.random() < 0.4:
        act_counter += 1
        amount = f_mean * random.uniform(0.1, 0.4)
        activities.append({
            'id': f'act-{uid}-{act_counter:03d}',
            'client_uid': uid,
            'client_name': name,
            'type': '理财到期',
            'sub_type': '',
            'amount_display': _fmt_amount(amount),
            'time_ago': random.choice(['今天', '明天', '3天后', '下周']),
        })

    # 大额盈利: 有交易业务 30% 概率
    if has_trading and random.random() < 0.3:
        act_counter += 1
        amount = abs(f_mean * random.uniform(0.02, 0.15))
        activities.append({
            'id': f'act-{uid}-{act_counter:03d}',
            'client_uid': uid,
            'client_name': name,
            'type': '大额盈利',
            'sub_type': '',
            'amount_display': _fmt_amount(amount),
            'time_ago': random.choice(['1小时前', '6小时前', '昨天']),
        })

    # 大额亏损: 有交易业务 30% 概率
    if has_trading and random.random() < 0.3:
        act_counter += 1
        amount = -abs(f_mean * random.uniform(0.02, 0.15))
        activities.append({
            'id': f'act-{uid}-{act_counter:03d}',
            'client_uid': uid,
            'client_name': name,
            'type': '大额亏损',
            'sub_type': '',
            'amount_display': _fmt_amount(amount),
            'time_ago': random.choice(['2小时前', '8小时前', '昨天']),
        })

    return events, activities


def build_mock_data(rows):
    clients = []
    all_events = []
    all_activities = []

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

        # Events & Activities
        uid = row["uid"]
        name = row["name"]
        client_events, client_activities = _generate_events_and_activities(
            uid, name, row["status"], f_mean, row,
        )
        all_events.extend(client_events)
        all_activities.extend(client_activities)

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
            "activities": client_activities,
        })

    by_id = {c["uid"]: c for c in clients}

    # Sort events by urgency then time
    all_events.sort(key=lambda e: _URGENCY_ORDER.get(e.get("urgency", "info"), 9))

    # Events by client UID lookup
    events_by_uid = {}
    for evt in all_events:
        cuid = evt["client_uid"]
        events_by_uid.setdefault(cuid, []).append(evt)

    # Activities by client UID lookup
    activities_by_uid = {}
    for act in all_activities:
        cuid = act["client_uid"]
        activities_by_uid.setdefault(cuid, []).append(act)

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
        "activities": all_activities,
        "activitiesByClientUid": activities_by_uid,
        "stats": {
            "total": len(clients),
            "churn": len(churn_list),
            "growth": len(growth_list),
            "stable": len(clients) - len(churn_list) - len(growth_list),
            "eventCount": len(all_events),
            "criticalEvents": sum(1 for e in all_events if e.get("urgency") == "critical"),
            "activityCount": len(all_activities),
        },
    }


def to_js(data):
    return f"window.PROTOTYPE_DATA = {json.dumps(data, ensure_ascii=False)};"
