#!/usr/bin/env python3
"""Shared mock data contract for Sales Hub prototype pages."""

from __future__ import annotations

import json
import math
import random
from collections import defaultdict


BD_OWNERS = ["李明远", "张晨", "王璐", "陈哲", "周宁"]
BD_TAG_POOL = [
    "英文沟通",
    "偏好短线",
    "消息响应快",
    "偏好语音",
    "机构决策慢",
    "重视返佣",
    "适合活动邀约",
    "需要高频维护",
]

EVENT_BLUEPRINTS = [
    ("evt-001", "出金预警", "大额出金预警", "未开始", "10分钟前"),
    ("evt-002", "充值", "首次合约充值", "未开始", "1小时前"),
    ("evt-003", "盈利", "本月盈利超阈值", "未开始", "3小时前"),
    ("evt-004", "爆仓", "大额爆仓警告", "跟进中", "昨天"),
    ("evt-005", "出金预警", "持续提现提醒", "跟进中", "昨天"),
    ("evt-006", "爆仓", "客户大额亏损", "已结束", "3天前"),
    ("evt-007", "人工", "账户长期未登录", "已结束", "4天前"),
    ("evt-008", "盈利", "理财到期未续", "已结束", "5天前"),
    ("evt-009", "人工", "邀约活动参与", "已忽略", "6天前"),
    ("evt-010", "人工", "手续费优惠到期", "已结束", "1周前"),
    ("evt-011", "盈利", "资产配置建议", "已结束", "1周前"),
    ("evt-012", "人工", "节日问候提醒", "已忽略", "2周前"),
]

STATE_STYLE = {
    "未开始": {"badgeBg": "#2D1B00", "badgeText": "#F0B90B"},
    "跟进中": {"badgeBg": "#0D1F2D", "badgeText": "#4DA6FF"},
    "已结束": {"badgeBg": "#0D2620", "badgeText": "#0ECB81"},
    "已忽略": {"badgeBg": "#1A1A1A", "badgeText": "#848E9C"},
}

TYPE_STYLE = {
    "出金预警": {"icon": "triangle-exclamation", "bg": "#2D1B1E", "fg": "#F6465D"},
    "爆仓": {"icon": "triangle-exclamation", "bg": "#2D1B1E", "fg": "#F6465D"},
    "盈利": {"icon": "bolt", "bg": "#2D2010", "fg": "#F0B90B"},
    "充值": {"icon": "bolt", "bg": "#2D2010", "fg": "#F0B90B"},
    "人工": {"icon": "circle-info", "bg": "#1E2329", "fg": "#848E9C"},
}


def client_detail_href(uid: str) -> str:
    return f"client-detail.html?uid={uid}"


def event_thread_href(event_id: str) -> str:
    return f"event-thread.html?event={event_id}"


def serialize_mock_data_js(data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"window.PROTOTYPE_DATA = {payload};\n"


def _fmt_n(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def _fmt_f(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value / 1_000:.0f}K"


def _fmt_pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _trend_delta(row: dict) -> float:
    rng = random.Random(int(float(row["E90"]) * 1_000_000) % 9999)
    return round(rng.uniform(-15, 25), 1)


def _owner_for(row: dict) -> str:
    return BD_OWNERS[int(row["uid"]) % len(BD_OWNERS)]


def _bd_tags_for(row: dict) -> list[str]:
    rng = random.Random(int(row["uid"]) + 17)
    return rng.sample(BD_TAG_POOL, 2)


def _note_for(row: dict) -> str:
    if row["label"] == "高潜客户":
        return "资沉足够但变现效率偏低，优先从理财和合约转化切入。"
    if row.get("tag") == "沉淀弱":
        return "贡献高但沉淀偏弱，近期重点关注资金留存和联系频次。"
    if row["value_source"] == "双仓合约":
        return "核心价值来自双仓合约，沟通节奏要贴合交易周期。"
    return "关系稳定，按月维护即可，关注近期资金流向变化。"


def _gift_for(row: dict) -> dict:
    budget = max(0, math.floor(float(row["N90"]) * 0.20))
    sent = math.floor(budget * 0.27)
    activated = math.floor(sent * 0.42)
    return {
        "ratio": "20%",
        "budget": budget,
        "budgetDisplay": _fmt_n(budget),
        "sent": sent,
        "sentDisplay": _fmt_n(sent),
        "activated": activated,
        "activatedDisplay": _fmt_n(activated),
        "remaining": max(budget - sent, 0),
        "remainingDisplay": _fmt_n(max(budget - sent, 0)),
        "activationRate": "42.0%",
    }


def _business_lines(row: dict) -> list[dict]:
    lines = [
        ("双仓合约", float(row["N_futures"])),
        ("超级杠杆", float(row["N_leverage"])),
        ("Mini合约", float(row["N_mini"])),
        ("金融卡", float(row["N_card"])),
        ("云算力", float(row["N_cloud"])),
        ("理财利息", float(row["N_savings"])),
        ("返佣支出", float(row["N_rebate"])),
    ]
    total_positive = sum(v for _, v in lines if v > 0) or 1.0
    items = []
    for name, value in lines:
        ratio = abs(value) / total_positive * 100
        items.append(
            {
                "name": name,
                "value": value,
                "valueDisplay": _fmt_n(value),
                "ratioDisplay": f"{'-' if value < 0 else ''}{ratio:.1f}%",
                "barPercent": min(round(ratio, 1), 100),
                "tone": "negative" if value < 0 else "positive",
            }
        )
    return items


def _records_for(row: dict) -> list[dict]:
    owner = _owner_for(row)
    return [
        {
            "time": "2026-03-28 11:45",
            "text": "与客户确认近期资产调动节奏，客户表示本周会继续保留主要仓位。",
            "author": owner,
        },
        {
            "time": "2026-03-25 16:20",
            "text": "同步了近期活动和理财权益，客户对手续费返券保持兴趣。",
            "author": owner,
        },
        {
            "time": "2026-03-20 09:10",
            "text": "例行维护沟通，确认主要交易仍集中在合约和杠杆。",
            "author": owner,
        },
    ]


def _system_tags_for(row: dict) -> list[str]:
    tags = []
    if row.get("subtype"):
        tags.append(row["subtype"])
    if row.get("tag"):
        tags.append(row["tag"])
    if row.get("value_source"):
        tags.append(row["value_source"])
    if row["label"] == "高潜客户":
        tags.append("高潜观察")
    elif row["label"] == "高价值客户":
        tags.append("高价值观察")
    return tags[:4]


def _current_assets_display(row: dict) -> str:
    return _fmt_f(float(row["F90"]) * 0.79)


def _pick_event_clients(rows: list[dict]) -> list[dict]:
    high_value = sorted(
        [row for row in rows if row["label"] == "高价值客户"],
        key=lambda item: item["N90"],
        reverse=True,
    )
    high_potential = sorted(
        [row for row in rows if row["label"] == "高潜客户"],
        key=lambda item: item["opportunity_gap"],
        reverse=True,
    )
    by_value = sorted(rows, key=lambda item: item["N90"], reverse=True)

    candidates = []
    for bucket in (
        high_value[:5],
        high_potential[:5],
        by_value[:12],
    ):
        for row in bucket:
            if row["uid"] not in {item["uid"] for item in candidates}:
                candidates.append(row)
            if len(candidates) >= len(EVENT_BLUEPRINTS):
                return candidates[: len(EVENT_BLUEPRINTS)]
    return candidates[: len(EVENT_BLUEPRINTS)]


def _event_summary(event_type: str, row: dict) -> str:
    if event_type == "出金预警":
        return f"{row['name']} · {_fmt_f(float(row['F90']) * 0.17)} 出金"
    if event_type == "充值":
        return f"{row['name']} · {_fmt_f(float(row['F90']) * 0.05)} 充入合约"
    if event_type == "盈利":
        return f"{row['name']} · 盈利{_fmt_n(max(float(row['N90']) * 0.18, 8000))}"
    if event_type == "爆仓":
        return f"{row['name']} · 爆仓{_fmt_n(max(float(row['N90']) * 0.22, 15000))}"
    return f"{row['name']} · 关系维护提醒"


def _event_suggestion(event_type: str, row: dict) -> str:
    if event_type == "出金预警":
        return "建议: 致电确认留存意向"
    if event_type == "充值":
        return "建议: 跟进合约体验与权益"
    if event_type == "盈利":
        return "建议: 借盈利窗口推介权益"
    if event_type == "爆仓":
        return "建议: 安抚情绪并确认后续计划"
    return "建议: 维持联系并补充上下文"


def _event_thread_payload(event_id: str, event_type: str, title: str, row: dict) -> dict:
    style = TYPE_STYLE[event_type]
    gift = _gift_for(row)
    metric_value = _fmt_f(float(row["F90"]) * 0.17)
    return {
        "id": event_id,
        "clientUid": row["uid"],
        "type": event_type,
        "title": title,
        "occurredAt": "2026-03-30 09:32",
        "metricPrimaryLabel": "关联金额",
        "metricPrimaryValue": metric_value,
        "metricSecondaryLabel": "当前资沉",
        "metricSecondaryValue": _current_assets_display(row),
        "rule": "规则：由统一 mock data 规则生成的演示事件",
        "aiSummary": f"{row['name']} 当前处于 {row['label']}，最近需要围绕“{title}”优先跟进。",
        "aiActions": [
            "先确认事件成因，再判断是流动性问题还是关系维护问题。",
            "结合客户当前价值来源，选择合适的话术和权益补充。",
            "记录结果并根据客户反馈调整下次动作。",
        ],
        "script": f"{row['name']}，您好！注意到您这边出现“{title}”信号，我想先确认一下当前安排，看看这边能否协助您更顺畅地处理资产和交易计划。",
        "followTimeline": _records_for(row),
        "voucher": {
            "ratioDisplay": gift["ratio"],
            "budgetDisplay": gift["budgetDisplay"],
            "budget": gift["budget"],
        },
        "icon": style["icon"],
        "iconBg": style["bg"],
        "iconColor": style["fg"],
    }


def build_mock_data(rows: list[dict]) -> dict:
    client_profiles = []
    clients_by_id = {}

    for row in rows:
        owner = _owner_for(row)
        profile = {
            "uid": row["uid"],
            "name": row["name"],
            "label": row["label"],
            "subtype": row.get("subtype", ""),
            "tag": row.get("tag", ""),
            "valueSource": row.get("value_source", ""),
            "recommend": row.get("recommend", ""),
            "reason": row.get("reason", ""),
            "n90": row["N90"],
            "f90": row["F90"],
            "e90": row["E90"],
            "opportunityGap": row["opportunity_gap"],
            "n90Display": _fmt_n(float(row["N90"])),
            "f90Display": _fmt_f(float(row["F90"])),
            "e90Display": _fmt_pct(float(row["E90"])),
            "opportunityGapDisplay": _fmt_n(float(row["opportunity_gap"])),
            "quarterTrendDisplay": f"{_trend_delta(row):+g}%",
            "currentAssetsDisplay": _current_assets_display(row),
            "bdOwner": owner,
            "onboardingDate": "2024.06",
            "systemTags": _system_tags_for(row),
            "bdTags": _bd_tags_for(row),
            "note": _note_for(row),
            "gift": _gift_for(row),
            "businessLines": _business_lines(row),
            "records": _records_for(row),
            "relatedEventIds": [],
            "detailHref": client_detail_href(row["uid"]),
        }
        client_profiles.append(profile)
        clients_by_id[row["uid"]] = profile

    events = []
    event_candidates = _pick_event_clients(rows)
    events_by_id = {}
    client_events = defaultdict(list)

    for blueprint, row in zip(EVENT_BLUEPRINTS, event_candidates):
        event_id, event_type, title, state, relative_time = blueprint
        style = TYPE_STYLE[event_type]
        summary = _event_summary(event_type, row)
        suggestion = _event_suggestion(event_type, row)
        event = {
            "id": event_id,
            "clientUid": row["uid"],
            "clientName": row["name"],
            "type": event_type,
            "title": title,
            "state": state,
            "relativeTime": relative_time,
            "summary": summary,
            "suggestion": suggestion,
            "href": event_thread_href(event_id),
            "badgeBg": STATE_STYLE[state]["badgeBg"],
            "badgeText": STATE_STYLE[state]["badgeText"],
            "icon": style["icon"],
            "iconBg": style["bg"],
            "iconColor": style["fg"],
            "thread": _event_thread_payload(event_id, event_type, title, row),
        }
        events.append(event)
        events_by_id[event_id] = event
        client_events[row["uid"]].append(event_id)

    for uid, event_ids in client_events.items():
        clients_by_id[uid]["relatedEventIds"] = event_ids[:3]

    high_value = sorted(
        [row for row in rows if row["label"] == "高价值客户"],
        key=lambda item: item["N90"],
        reverse=True,
    )
    high_potential = sorted(
        [row for row in rows if row["label"] == "高潜客户"],
        key=lambda item: item["opportunity_gap"],
        reverse=True,
    )

    default_client_uid = high_value[0]["uid"] if high_value else rows[0]["uid"]
    default_event_id = events[0]["id"] if events else ""

    return {
        "generatedAt": "2026-03-30",
        "defaultClientUid": default_client_uid,
        "defaultEventId": default_event_id,
        "highValueUids": [row["uid"] for row in high_value],
        "highPotentialUids": [row["uid"] for row in high_potential],
        "clients": client_profiles,
        "clientsById": clients_by_id,
        "events": events,
        "eventsById": events_by_id,
    }
