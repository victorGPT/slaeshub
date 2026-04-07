"""Regression coverage for event creation/detail UI in client detail prototype."""

from pathlib import Path


HTML_PATH = Path("/Users/victor/Developer/slaeshub/prototype/client-detail.html")


def _html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


def test_create_task_sheet_supports_event_type_note_and_watch_controls():
    html = _html()
    assert "添加事件" in html
    assert "+ 添加事件" in html
    assert "主动联系" in html
    assert "客户反馈" in html
    assert ">其他<" in html
    assert "事件说明" in html
    assert "记录一下..." in html
    assert "提醒关注" in html
    assert "有截止日期或需持续跟进时开启，事件将置顶显示" in html
    assert "今天" in html
    assert "本周" in html
    assert "自定义时间" not in html
    assert "将在 X月X日 提醒关注" in html
    assert 'type="date"' in html
    assert 'type="time"' not in html


def test_event_logic_uses_note_with_legacy_text_fallback_and_watch_until():
    html = _html()
    assert "t.note || t.text" in html
    assert "selectedType" in html
    assert "watchUntil" in html
    assert "selectedWatchPreset" in html
    assert "watchEnabled" in html
    assert "getWeekFridayDateKey" in html
    assert "selectedWatchTimePreset" not in html
    assert "customWatchTime" not in html
    assert "remindAt" not in html


def test_event_card_and_detail_render_type_and_watch_status():
    html = _html()
    assert "task-detail-type" in html
    assert "task-detail-watch" in html
    assert "关注至" in html
    assert "已逾期" in html
    assert "3天内" in html or "3 * 24 * 60 * 60 * 1000" in html
    assert "font-size:10px" in html


def test_event_list_is_single_stream_with_watch_first_and_archived_last():
    html = _html()
    assert "taskTab" not in html
    assert "switchTaskTab" not in html
    assert "暂无归档事件" not in html
    assert "withWatch" in html
    assert "withoutWatch" in html
    assert "archived" in html
    assert "aWatch.expireAt.getTime() - bWatch.expireAt.getTime()" in html
    assert "bDate.getTime() - aDate.getTime()" in html
    assert "height:1px;background:#2E3440;margin:4px 0 8px" in html
    assert "opacity:0.45" in html
    assert "line-through" in html
