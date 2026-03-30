#!/usr/bin/env python3
"""
Sales Hub — 原型数据注入脚本
读取 clients_simulation.csv，用真实模拟数据替换原型 HTML 里的假数据。

生成：
  - prototype/mock-data.js  共享运行时数据
  - home-a.html             高价值 Top5（综合）+ 高潜 Top3
  - home-b.html             高价值（综合/现货/合约子Tab）+ 高潜 Top3
  - home-c.html             两行列表版
  - clients.html            全量 100 客户
"""

import csv, os, math

from prototype_data import build_mock_data, client_detail_href, serialize_mock_data_js

BASE  = '/Users/victor/Developer/slaeshub'
CSV   = f'{BASE}/data/clients_simulation.csv'
PROTO = f'{BASE}/prototype'

# ─── 读取并排序 ───────────────────────────────────────────────────
def load():
    with open(CSV, encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r['N90']             = float(r['N90'])
        r['F90']             = float(r['F90'])
        r['E90']             = float(r['E90'])
        r['opportunity_gap'] = float(r['opportunity_gap'])
        r['N_futures']       = float(r['N_futures'])
        r['N_leverage']      = float(r['N_leverage'])
        r['X_futures_days']  = int(r['X_futures_days'])
        r['X_savings_bal']   = float(r['X_savings_bal'])
    return rows

def fmt_n(v):
    if abs(v) >= 1_000_000: return f'${v/1_000_000:.2f}M'
    if abs(v) >= 1_000:     return f'${v/1_000:.1f}K'
    return f'${v:.0f}'

def fmt_f(v):
    if v >= 1_000_000: return f'${v/1_000_000:.1f}M'
    return f'${v/1_000:.0f}K'

def trend_html(e90, baseline=0.01):
    """周环比用 E90 相对变化模拟（原型用）"""
    import random; random.seed(int(e90 * 1e6) % 9999)
    pct = round(random.uniform(-15, 25), 1)
    if pct > 0:
        return f'<span class="text-[11px] text-[#0ECB81] font-medium">▲{pct}%</span>'
    elif pct < 0:
        return f'<span class="text-[11px] text-[#F6465D] font-medium">▼{abs(pct)}%</span>'
    return '<span class="text-[11px] text-[#848E9C] font-medium">— 持平</span>'

def tag_html(tag_str, subtype):
    """Tag pill HTML"""
    tags = [t.strip() for t in tag_str.split(',') if t.strip()] if tag_str else []
    # 子类型 tag
    if subtype == '贡献达标型':
        tags.insert(0, '贡献达标')
    elif subtype == '沉淀优质型':
        tags.insert(0, '沉淀优质')
    # 辅助标签（沉淀强/弱 单独处理，在外层加）
    html = ''
    for t in tags[:2]:
        html += f'<span class="bg-[#2D2010] text-[#F0B90B] text-[10px] px-1.5 py-0.5 rounded-full">{t}</span>\n            '
    return html

def recommend_short(rec):
    """缩短推荐方向文字"""
    rec = rec.replace('（现有资沉未用于交易）','').replace('（资产沉淀可转化）','').replace('（合约用户自然延伸）','').replace('（提升资金粘性）','').replace('（交易渗透不足）','')
    return rec.strip()

# ─── HTML 片段生成 ────────────────────────────────────────────────

HEAD = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Sales Hub – {title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'hub-bg':'#0B0E11','hub-card':'#1E2329','hub-card-hover':'#2B3139',
            'hub-border':'#2E3440','hub-gold':'#F0B90B','hub-gold-text':'#F8D33A',
            'hub-red':'#F6465D','hub-green':'#0ECB81','hub-blue':'#4DA6FF',
            'hub-text':'#EAECEF','hub-muted':'#848E9C','hub-disabled':'#474D57',
          }}
        }}
      }}
    }}
  </script>
  <style>
    body {{ font-family: 'PingFang SC','Helvetica Neue',sans-serif; background:#0B0E11; }}
    ::-webkit-scrollbar {{ display:none; }}
    html {{ background:#000; }}
    html, body {{ width:393px !important; margin:0 auto !important; overflow-x:hidden; }}
    .fixed-bar {{ position:fixed; bottom:0; left:50%; transform:translateX(-50%); width:393px; }}
  </style>
</head>
<body class="bg-[#0B0E11] text-[#EAECEF]">
<div class="w-full">
  <!-- 状态栏 -->
  <div class="h-[44px] bg-[#0B0E11] flex items-center justify-between px-6">
    <span class="text-[12px] font-semibold">9:41</span>
    <div class="flex items-center gap-1.5">
      <i class="fa-solid fa-signal text-[12px]"></i>
      <i class="fa-solid fa-wifi text-[12px]"></i>
      <i class="fa-solid fa-battery-full text-[13px]"></i>
    </div>
  </div>
  <!-- 顶部导航 -->
  <div class="h-[52px] sticky top-0 z-10 bg-[#0B0E11] border-b border-[#2E3440] flex items-center justify-between px-4">
    <div class="w-[60px]"></div>
    <h1 class="text-[17px] font-bold text-[#EAECEF] tracking-wide">Sales Hub</h1>
    <div class="flex items-center gap-4">
      <i class="fa-solid fa-magnifying-glass text-[#848E9C] text-[16px]"></i>
      <div class="relative">
        <i class="fa-solid fa-bell text-[#848E9C] text-[16px]"></i>
        <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#F6465D]"></span>
      </div>
    </div>
  </div>
  <!-- 顶部 Tab -->
  <div class="flex border-b border-[#2E3440] bg-[#0B0E11] sticky top-[52px] z-10">
    <button onclick="switchTab('high')" id="tab-high"
      class="flex-1 py-3 text-[14px] font-semibold text-[#F0B90B] border-b-2 border-[#F0B90B]">高价值客户</button>
    <button onclick="switchTab('develop')" id="tab-develop"
      class="flex-1 py-3 text-[14px] text-[#848E9C]">高潜客户</button>
  </div>
  <!-- 内容区 -->
  <div class="overflow-y-auto pb-[90px]" style="scrollbar-width:none;">
'''

TAIL = '''
  </div>
  <!-- 底部 Tab -->
  <div class="fixed-bar bg-[#0B0E11] border-t border-[#2E3440] z-20">
    <div class="flex items-center justify-around h-[56px]">
      <a href="{home_link}" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-house text-[#F0B90B] text-[18px]"></i>
        <span class="text-[10px] text-[#F0B90B] font-medium">首页</span>
      </a>
      <a href="clients.html" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-users text-[#848E9C] text-[18px]"></i>
        <span class="text-[10px] text-[#848E9C]">客群</span>
      </a>
      <a href="events.html" class="flex flex-col items-center gap-0.5">
        <div class="relative">
          <i class="fa-solid fa-bell text-[#848E9C] text-[18px]"></i>
          <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#F6465D]"></span>
        </div>
        <span class="text-[10px] text-[#848E9C]">事件</span>
      </a>
      <a href="profile.html" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-circle-user text-[#848E9C] text-[18px]"></i>
        <span class="text-[10px] text-[#848E9C]">我的</span>
      </a>
    </div>
    <div class="h-[34px]"></div>
  </div>
</div>
<script>
  sessionStorage.setItem('homeVersion', '{version}');
  function switchTab(t) {{
    ['high','develop'].forEach(id => {{
      document.getElementById('panel-' + id).classList.toggle('hidden', id !== t);
      document.getElementById('tab-' + id).className = id === t
        ? 'flex-1 py-3 text-[14px] font-semibold text-[#F0B90B] border-b-2 border-[#F0B90B]'
        : 'flex-1 py-3 text-[14px] text-[#848E9C]';
    }});
  }}
  {extra_js}
</script>
</body>
</html>
'''

def gen_action_status(r):
    """生成行动状态：(dot_color_class, status_text, status_text_color)
    dot_color_class: Tailwind bg class 或 '' 表示无点
    """
    import random as _r
    _r.seed(int(r['uid']) % 77777)
    tag   = r.get('tag', '')
    label = r.get('label', '')

    # 高价值沉淀弱：较高概率有待处理事件
    if label == '高价值客户' and tag == '沉淀弱':
        roll = _r.random()
        if roll < 0.55:
            n = _r.randint(1, 3)
            return 'bg-[#F6465D]', f'{n}条待处理', '#F6465D'
        elif roll < 0.75:
            return 'bg-[#4DA6FF]', '跟进中', '#4DA6FF'
        else:
            days = _r.randint(1, 14)
            return '', f'{days}天前跟进', '#474D57'

    # 高潜客户：有待处理事件
    elif label == '高潜客户':
        roll = _r.random()
        if roll < 0.5:
            n = _r.randint(1, 2)
            return 'bg-[#F6465D]', f'{n}条待处理', '#F6465D'
        elif roll < 0.65:
            return 'bg-[#4DA6FF]', '跟进中', '#4DA6FF'
        else:
            days = _r.randint(2, 21)
            return '', f'{days}天前跟进', '#474D57'

    # 高价值沉淀强：多数情况已跟进
    elif label == '高价值客户':
        roll = _r.random()
        if roll < 0.25:
            n = _r.randint(1, 2)
            return 'bg-[#F6465D]', f'{n}条待处理', '#F6465D'
        elif roll < 0.4:
            return 'bg-[#4DA6FF]', '跟进中', '#4DA6FF'
        elif roll < 0.75:
            days = _r.randint(1, 30)
            return '', f'{days}天前跟进', '#474D57'
        else:
            return '', '', ''  # 未建联

    # 非主榜：多数未建联
    else:
        roll = _r.random()
        if roll < 0.15:
            return 'bg-[#F6465D]', '1条待处理', '#F6465D'
        elif roll < 0.35:
            days = _r.randint(3, 60)
            return '', f'{days}天前跟进', '#474D57'
        else:
            return '', '', ''  # 未建联


def gen_nickname(r, rank):
    """BD 备注（昵称）：前30名高频客户由 BD 手动填过，其余默认无"""
    # 用原始 name 字段作为模拟的 BD 备注，但只给前30名和所有高价值/高潜客户
    label = r.get('label', '')
    if rank <= 15 or label in ('高价值客户', '高潜客户'):
        return r.get('name', '')
    return ''  # 未填备注，只显示 UID


def maintenance_hint(r):
    """高价值客户维护建议——关注关系稳定，而非业务推荐"""
    tag    = r.get('tag', '')
    e90    = r['E90']
    sub    = r.get('subtype', '')
    f90    = r['F90']
    n90    = r['N90']

    if tag == '沉淀弱' and e90 > 0.04:
        return f"贡献突出但资沉仅 {fmt_f(f90)}，流失风险高——本周优先致电维护"
    if tag == '沉淀弱':
        return f"资沉偏低，建议本周致电了解资金动向，加强关系绑定"
    if sub == '沉淀优质型':
        return f"资金沉淀健康、变现效率稳定，定期维护即可"
    if e90 > 0.06:
        return f"高频交易客户，效率 {e90*100:.1f}%，注意情绪波动，保持高频联系"
    if e90 > 0.02:
        return f"贡献稳定，本月安排一次常规维护通话"
    return f"关系底盘良好，关注近期资金动态变化"


def gen_signals(r):
    """基于客户数据生成差异化信号 badge（确定性，用 UID 作种子）"""
    import random as _r
    _r.seed(int(r['uid']) % 99991)

    signals = []

    # 信号1：待处理事件数（沉淀弱客户概率更高）
    tag = r.get('tag', '')
    event_prob = 0.55 if tag == '沉淀弱' else 0.20
    if _r.random() < event_prob:
        count = _r.randint(1, 3) if tag == '沉淀弱' else 1
        signals.append(('event', count))

    # 信号2：距上次联系天数（超过阈值才显示）
    days = _r.randint(5, 65)
    if days > 30:
        signals.append(('contact', days))

    # 信号3：N90 趋势下滑（复用 trend_html 的种子逻辑）
    import random as _r2
    _r2.seed(int(r['E90'] * 1e6) % 9999)
    pct = round(_r2.uniform(-15, 25), 1)
    if pct < -8:
        signals.append(('trend', pct))

    return signals


def signal_badges_html(signals):
    """把信号列表转成 badge HTML，无信号返回空字符串"""
    html = ''
    for sig_type, val in signals:
        if sig_type == 'event':
            html += f'<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full font-medium">事件×{val}</span>\n            '
        elif sig_type == 'contact':
            if val > 45:
                html += f'<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full">{val}天未联系</span>\n            '
            else:
                html += f'<span class="bg-[#2D1B00] text-[#F0B90B] text-[10px] px-1.5 py-0.5 rounded-full">{val}天未联系</span>\n            '
        elif sig_type == 'trend':
            html += f'<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full">趋势下滑</span>\n            '
    return html


def avatar_url(name):
    import urllib.parse
    return f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=2B3139&color=EAECEF&size=40&font-size=0.4&bold=true"

def rank_color(i):
    if i <= 3: return '#F0B90B'
    return '#848E9C'

def border_style(i):
    if i <= 3: return 'border-2 border-[#F0B90B]'
    return ''

# ─── 卡片版 card (Version A / B) ──────────────────────────────────
def hv_card(r, i):
    tag = r.get('tag', '')
    tag_pill = ''
    if tag == '沉淀弱':
        tag_pill = '<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full">沉淀弱</span>'
    elif tag == '沉淀强':
        tag_pill = '<span class="bg-[#0D1F2D] text-[#4DA6FF] text-[10px] px-1.5 py-0.5 rounded-full">沉淀强</span>'

    subtype_pill = ''
    if r['subtype'] == '沉淀优质型':
        subtype_pill = '<span class="bg-[#0D2620] text-[#0ECB81] text-[10px] px-1.5 py-0.5 rounded-full">沉淀优质</span>'

    trend = trend_html(r['E90'])
    border = border_style(i)
    rc = rank_color(i)
    signals = gen_signals(r)
    sig_html = signal_badges_html(signals)

    return f'''        <a href="{client_detail_href(r['uid'])}" class="block bg-[#1E2329] rounded-xl border border-[#2E3440] p-4 mx-4 mb-2 active:bg-[#2B3139]">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-[13px] font-bold w-6 flex-shrink-0" style="color:{rc}">#{i}</span>
            <img src="{avatar_url(r['name'])}" class="w-10 h-10 rounded-full {border} flex-shrink-0" />
            <span class="flex-1 text-[14px] font-semibold text-[#EAECEF]">{r['name']}</span>
            <span class="text-[11px] text-[#474D57]">{r['uid']}</span>
          </div>
          <div class="flex flex-wrap gap-1 mb-2">
            {tag_pill}
            {subtype_pill}
            {sig_html}
          </div>
          <div class="flex items-baseline gap-2 mb-1">
            <span class="text-[11px] text-[#848E9C]">综合净贡献</span>
            <span class="text-[20px] font-bold text-[#F8D33A]">{fmt_n(r['N90'])}</span>
            {trend}
          </div>
          <div class="flex items-center gap-2">
            <span class="text-[11px] text-[#848E9C]">资沉</span>
            <span class="text-[14px] text-[#EAECEF]">{fmt_f(r['F90'])}</span>
            <span class="text-[11px] text-[#848E9C]">效率</span>
            <span class="text-[11px] text-[#EAECEF]">{r['E90']*100:.2f}%</span>
          </div>
        </a>
'''

def hp_card(r, i):
    trend = trend_html(r['E90'])
    gap_pct = (r['E90'] / 0.003) * 100  # 相对变现均线的进度
    bar_w = min(int(gap_pct), 100)
    rec = recommend_short(r['recommend'])

    return f'''        <a href="{client_detail_href(r['uid'])}" class="block bg-[#1E2329] rounded-xl border border-[#2E3440] p-4 mx-4 mb-2 active:bg-[#2B3139]">
          <div class="flex items-center gap-3 mb-2">
            <span class="text-[13px] font-bold text-[#4DA6FF] w-6 flex-shrink-0">#{i}</span>
            <img src="{avatar_url(r['name'])}" class="w-10 h-10 rounded-full border-2 border-[#4DA6FF] flex-shrink-0" />
            <span class="flex-1 text-[14px] font-semibold text-[#EAECEF]">{r['name']}</span>
            <span class="text-[11px] text-[#474D57]">{r['uid']}</span>
          </div>
          <div class="flex items-baseline gap-2 mb-1">
            <span class="text-[11px] text-[#848E9C]">日均资沉</span>
            <span class="text-[18px] font-bold text-[#F8D33A]">{fmt_f(r['F90'])}</span>
          </div>
          <div class="flex items-center gap-2 mb-1">
            <span class="text-[11px] text-[#848E9C]">效率</span>
            <div class="flex-1 h-1 rounded-full bg-[#2E3440]">
              <div class="h-1 rounded-full bg-[#F0B90B]" style="width:{bar_w}%"></div>
            </div>
            <span class="text-[10px] text-[#F6465D]">{r['E90']*100:.2f}%</span>
          </div>
          <div class="flex items-center gap-2 mb-2">
            <span class="text-[11px] text-[#848E9C]">机会缺口</span>
            <span class="text-[13px] font-semibold text-[#F0B90B]">{fmt_n(r['opportunity_gap'])}</span>
            <span class="text-[10px] text-[#848E9C]">（按变现均线估算）</span>
          </div>
          <p class="text-[12px] text-[#F0B90B] truncate">推荐方向：{rec} →</p>
        </a>
'''

# ─── 列表行 (Version C) ────────────────────────────────────────────
def hv_row(r, i, last=False):
    border = '' if last else 'border-b border-[#2E3440]'
    rc = rank_color(i)
    trend = trend_html(r['E90'])
    tag = r.get('tag', '')
    tag_html_str = ''
    if tag == '沉淀弱':
        tag_html_str = '<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full">沉淀弱</span>'
    elif tag == '沉淀强':
        tag_html_str = '<span class="bg-[#0D1F2D] text-[#4DA6FF] text-[10px] px-1.5 py-0.5 rounded-full">沉淀强</span>'
    signals = gen_signals(r)
    sig_html = signal_badges_html(signals)
    return f'''        <a href="{client_detail_href(r['uid'])}" class="flex items-center px-4 py-3 {border} active:bg-[#2B3139]">
          <span class="text-[12px] font-bold w-6 flex-shrink-0" style="color:{rc}">#{i}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
              <span class="text-[14px] font-semibold text-[#EAECEF]">{r['name']}</span>
              <span class="text-[11px] text-[#474D57]">{r['uid']}</span>
              <span class="text-[13px] font-bold text-[#F8D33A]">{fmt_n(r['N90'])}</span>
              {trend}
              {tag_html_str}
              {sig_html}
            </div>
            <p class="text-[11px] text-[#848E9C]">资沉 {fmt_f(r['F90'])} · 效率 {r['E90']*100:.2f}%</p>
          </div>
        </a>
'''

def hp_row(r, i, last=False):
    border = '' if last else 'border-b border-[#2E3440]'
    rec = recommend_short(r['recommend'])
    bar_w = min(int((r['E90'] / 0.003) * 100), 100)
    return f'''        <a href="{client_detail_href(r['uid'])}" class="flex items-center px-4 py-3 {border} active:bg-[#2B3139]">
          <span class="text-[12px] font-bold text-[#4DA6FF] w-6 flex-shrink-0">#{i}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
              <span class="text-[14px] font-semibold text-[#EAECEF]">{r['name']}</span>
              <span class="text-[11px] text-[#474D57]">{r['uid']}</span>
              <span class="text-[13px] font-bold text-[#F8D33A]">{fmt_f(r['F90'])}</span>
              <div class="flex items-center gap-1">
                <div class="w-10 h-1 rounded-full bg-[#2E3440]">
                  <div class="h-1 rounded-full bg-[#F0B90B]" style="width:{bar_w}%"></div>
                </div>
                <span class="text-[10px] text-[#F6465D]">{r['E90']*100:.2f}%</span>
              </div>
              <span class="text-[10px] text-[#F0B90B]">缺口{fmt_n(r['opportunity_gap'])}</span>
            </div>
            <p class="text-[11px] text-[#F0B90B] truncate">推荐：{rec} →</p>
          </div>
        </a>
'''

# ─── 查看全部按钮 ──────────────────────────────────────────────────
def see_all(tab, text):
    return f'''        <a href="clients.html?tab={tab}" class="flex items-center justify-between px-4 py-3 mb-1">
          <span class="text-[13px] text-[#848E9C]">{text}</span>
          <i class="fa-solid fa-chevron-right text-[#474D57] text-xs"></i>
        </a>
'''

# ─── 生成 home-a.html ──────────────────────────────────────────────
def gen_home_a(hv, hp):
    body = HEAD.format(title='首页 (A)')

    # 高价值 panel
    body += '    <div id="panel-high">\n'
    body += '      <div class="px-4 pt-3 pb-1"><p class="text-[11px] text-[#848E9C]">近90天综合净贡献排行 · 按 N90 降序</p></div>\n'
    for i, r in enumerate(hv[:5], 1):
        body += hv_card(r, i)
    body += see_all('all', f'查看全部高价值客户（共{len(hv)}人）')
    body += '    </div>\n'

    # 高潜 panel
    body += '    <div id="panel-develop" class="hidden">\n'
    body += '      <div class="px-4 pt-3 pb-1"><p class="text-[11px] text-[#848E9C]">按机会缺口排序 · F90×(T_E−E90)</p></div>\n'
    for i, r in enumerate(hp[:3], 1):
        body += hp_card(r, i)
    body += see_all('develop', f'查看全部高潜客户（共{len(hp)}人）')
    body += '    </div>\n'

    body += TAIL.format(home_link='home-a.html', version='a', extra_js='')
    return body

# ─── 生成 home-b.html（含现货/合约子Tab）──────────────────────────
def gen_home_b(hv, hp, all_rows):
    # 现货榜：按 X_futures_days 排序（活跃天数代理）
    spot = sorted([r for r in all_rows if r['X_futures_days'] > 0],
                  key=lambda x: x['X_futures_days'], reverse=True)[:5]
    # 合约榜：按 N_futures 排序
    futures = sorted([r for r in all_rows if r['N_futures'] > 0],
                     key=lambda x: x['N_futures'], reverse=True)[:5]

    body = HEAD.format(title='首页 (B)')

    body += '    <div id="panel-high">\n'
    # 子 Tab
    body += '''      <div class="flex gap-2 px-4 pt-3 pb-2">
        <button onclick="switchSub(\'all\')" id="sub-all" class="text-xs px-3 py-1.5 rounded-full bg-[#F0B90B] text-[#0B0E11] font-semibold">综合</button>
        <button onclick="switchSub(\'spot\')" id="sub-spot" class="text-xs px-3 py-1.5 rounded-full bg-[#2B3139] text-[#848E9C]">现货活跃</button>
        <button onclick="switchSub(\'futures\')" id="sub-futures" class="text-xs px-3 py-1.5 rounded-full bg-[#2B3139] text-[#848E9C]">合约贡献</button>
      </div>\n'''

    # 综合
    body += '      <div id="sub-all">\n'
    body += '      <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">近90天综合净贡献 N90 排行</p></div>\n'
    for i, r in enumerate(hv[:5], 1):
        body += hv_card(r, i)
    body += see_all('all', f'查看全部高价值客户（共{len(hv)}人）')
    body += '      </div>\n'

    # 现货活跃
    body += '      <div id="sub-spot" class="hidden">\n'
    body += '      <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">近90天现货活跃天数排行（X_futures_days）</p></div>\n'
    for i, r in enumerate(spot, 1):
        body += hv_card(r, i)
    body += '      </div>\n'

    # 合约贡献
    body += '      <div id="sub-futures" class="hidden">\n'
    body += '      <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">近90天双仓合约净贡献排行</p></div>\n'
    for i, r in enumerate(futures, 1):
        body += hv_card(r, i)
    body += '      </div>\n'

    body += '    </div>\n'  # /panel-high

    # 高潜 panel
    body += '    <div id="panel-develop" class="hidden">\n'
    body += '      <div class="px-4 pt-3 pb-1"><p class="text-[11px] text-[#848E9C]">按机会缺口排序 · 理论贡献−实际贡献</p></div>\n'
    for i, r in enumerate(hp[:3], 1):
        body += hp_card(r, i)
    body += see_all('develop', f'查看全部高潜客户（共{len(hp)}人）')
    body += '    </div>\n'

    extra_js = """
  function switchSub(t) {
    ['all','spot','futures'].forEach(id => {
      document.getElementById('sub-' + id).classList.toggle('hidden', id !== t);
      document.getElementById('sub-' + id + (id===t?'':'')).className;
      const btn = document.getElementById('sub-' + id);
      if(!btn) return;
    });
    ['all','spot','futures'].forEach(id => {
      const btn = document.getElementById('sub-' + id);
      btn.className = id === t
        ? 'text-xs px-3 py-1.5 rounded-full bg-[#F0B90B] text-[#0B0E11] font-semibold'
        : 'text-xs px-3 py-1.5 rounded-full bg-[#2B3139] text-[#848E9C]';
      document.getElementById('sub-' + id).classList.toggle('hidden', id !== t);
    });
  }"""

    body += TAIL.format(home_link='home-b.html', version='b', extra_js=extra_js)
    return body

# ─── 生成 home-c.html（两行列表）─────────────────────────────────
def gen_home_c(hv, hp):
    body = HEAD.format(title='首页 (C)')

    body += '    <div id="panel-high">\n'
    body += '      <div class="px-4 pt-3 pb-1"><p class="text-[11px] text-[#848E9C]">近90天综合净贡献排行 · 高密度列表</p></div>\n'
    body += '      <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mb-2">\n'
    for i, r in enumerate(hv[:7], 1):
        body += hv_row(r, i, last=(i == min(7, len(hv))))
    body += '      </div>\n'
    body += see_all('all', f'查看全部高价值客户（共{len(hv)}人）')
    body += '    </div>\n'

    body += '    <div id="panel-develop" class="hidden">\n'
    body += '      <div class="px-4 pt-3 pb-1"><p class="text-[11px] text-[#848E9C]">按机会缺口排序 · 变现空间最大优先</p></div>\n'
    body += '      <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mb-2">\n'
    for i, r in enumerate(hp[:5], 1):
        body += hp_row(r, i, last=(i == min(5, len(hp))))
    body += '      </div>\n'
    body += see_all('develop', f'查看全部高潜客户（共{len(hp)}人）')
    body += '    </div>\n'

    body += TAIL.format(home_link='home-c.html', version='c', extra_js='')
    return body

# ─── 生成 clients.html（全量）──────────────────────────────────────
def gen_clients(all_rows, hv, hp):
    all_sorted  = sorted(all_rows, key=lambda x: x['N90'], reverse=True)
    hp_sorted   = sorted(hp, key=lambda x: x['opportunity_gap'], reverse=True)
    fut_sorted  = sorted([r for r in all_rows if r['N_futures'] > 0],
                         key=lambda x: x['N_futures'], reverse=True)
    spot_sorted = sorted([r for r in all_rows if r['X_futures_days'] > 0],
                         key=lambda x: x['X_futures_days'], reverse=True)

    def client_row_html(r, i, last=False):
        border = '' if last else 'border-b border-[#2E3440]'
        trend = trend_html(r['E90'])
        tag = r.get('tag', '')
        tag_html_str = ''
        if tag == '沉淀弱':
            tag_html_str = '<span class="bg-[#2D1B1E] text-[#F6465D] text-[10px] px-1.5 py-0.5 rounded-full">沉淀弱</span>'
        elif tag == '沉淀强':
            tag_html_str = '<span class="bg-[#0D1F2D] text-[#4DA6FF] text-[10px] px-1.5 py-0.5 rounded-full">沉淀强</span>'

        # 行动状态：色点 + 状态文字
        dot_cls, status_text, status_color = gen_action_status(r)
        dot_html = f'<span class="w-2 h-2 rounded-full {dot_cls} flex-shrink-0 mr-1"></span>' if dot_cls else '<span class="w-2 h-2 flex-shrink-0 mr-1"></span>'
        status_html = f'<span class="text-[10px]" style="color:{status_color}">{status_text}</span>' if status_text else ''

        # UID 为主，BD 备注为辅
        nickname = gen_nickname(r, i)
        name_html = f'<span class="text-[13px] font-semibold text-[#EAECEF]">{nickname}</span>' if nickname else ''
        uid_html  = f'<span class="text-[12px] {"text-[#848E9C]" if nickname else "font-semibold text-[#EAECEF]"}">{r["uid"]}</span>'

        return f'''        <div data-uid="{r['uid']}" onclick="location.href='{client_detail_href(r['uid'])}'"
          class="flex items-center px-4 py-3 {border} active:bg-[#2B3139] cursor-pointer">
          {dot_html}
          <span class="text-[11px] text-[#474D57] w-6 flex-shrink-0">#{i}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
              {uid_html}
              {name_html}
              <span class="text-[13px] font-bold text-[#F8D33A]">{fmt_n(r['N90'])}</span>
              {trend}
              {tag_html_str}
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[11px] text-[#848E9C]">资沉 {fmt_f(r['F90'])}</span>
              {status_html}
            </div>
          </div>
          <button onclick="event.stopPropagation();toggleStar('{r['uid']}')"
            class="ml-2 w-7 h-8 flex items-center justify-center flex-shrink-0">
            <i id="star-{r['uid']}" class="fa-regular fa-star text-[#474D57] text-[14px]"></i>
          </button>
        </div>
'''

    def hp_row_clients(r, i, last=False):
        border = '' if last else 'border-b border-[#2E3440]'
        rec = recommend_short(r['recommend'])
        dot_cls, status_text, status_color = gen_action_status(r)
        dot_html = f'<span class="w-2 h-2 rounded-full {dot_cls} flex-shrink-0 mr-1"></span>' if dot_cls else '<span class="w-2 h-2 flex-shrink-0 mr-1"></span>'
        status_html = f'<span class="text-[10px]" style="color:{status_color}">{status_text}</span>' if status_text else ''
        nickname = gen_nickname(r, i)
        name_html = f'<span class="text-[13px] font-semibold text-[#EAECEF]">{nickname}</span>' if nickname else ''
        uid_html  = f'<span class="text-[12px] {"text-[#848E9C]" if nickname else "font-semibold text-[#EAECEF]"}">{r["uid"]}</span>'
        return f'''        <div data-uid="{r['uid']}" onclick="location.href='{client_detail_href(r['uid'])}'"
          class="flex items-center px-4 py-3 {border} active:bg-[#2B3139] cursor-pointer">
          {dot_html}
          <span class="text-[11px] text-[#4DA6FF] font-bold w-6 flex-shrink-0">#{i}</span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5 mb-0.5 flex-wrap">
              {uid_html}
              {name_html}
              <span class="text-[13px] font-bold text-[#F8D33A]">{fmt_f(r['F90'])}</span>
              <span class="text-[10px] text-[#F0B90B]">缺口{fmt_n(r['opportunity_gap'])}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[11px] text-[#848E9C]">推荐：{rec}</span>
              {status_html}
            </div>
          </div>
          <button onclick="event.stopPropagation();toggleStar('{r['uid']}')"
            class="ml-2 w-7 h-8 flex items-center justify-center flex-shrink-0">
            <i id="star-{r['uid']}" class="fa-regular fa-star text-[#474D57] text-[14px]"></i>
          </button>
        </div>
'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <title>Sales Hub – 客群</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {{
      theme: {{ extend: {{ colors: {{
        'hub-bg':'#0B0E11','hub-card':'#1E2329','hub-card-hover':'#2B3139',
        'hub-border':'#2E3440','hub-gold':'#F0B90B','hub-gold-text':'#F8D33A',
        'hub-red':'#F6465D','hub-green':'#0ECB81','hub-blue':'#4DA6FF',
        'hub-text':'#EAECEF','hub-muted':'#848E9C','hub-disabled':'#474D57',
      }} }} }}
    }}
  </script>
  <style>
    body {{ font-family:'PingFang SC','Helvetica Neue',sans-serif; background:#0B0E11; }}
    ::-webkit-scrollbar {{ display:none; }}
    html {{ background:#000; }}
    html, body {{ width:393px !important; margin:0 auto !important; overflow-x:hidden; }}
    .fixed-bar {{ position:fixed; bottom:0; left:50%; transform:translateX(-50%); width:393px; }}
    .pill-active {{ background:#F0B90B; color:#0B0E11; font-weight:600; }}
    .pill-inactive {{ background:#2B3139; color:#848E9C; }}
  </style>
</head>
<body class="bg-[#0B0E11] text-[#EAECEF]">
<div class="w-full">
  <div class="h-[44px] bg-[#0B0E11] flex items-center justify-between px-6">
    <span class="text-[12px] font-semibold">9:41</span>
    <div class="flex items-center gap-1.5">
      <i class="fa-solid fa-signal text-[12px]"></i>
      <i class="fa-solid fa-wifi text-[12px]"></i>
      <i class="fa-solid fa-battery-full text-[13px]"></i>
    </div>
  </div>
  <div class="h-[52px] sticky top-0 z-20 bg-[#0B0E11] border-b border-[#2E3440] flex items-center justify-between px-4">
    <div class="w-8"></div>
    <h1 class="text-[17px] font-bold text-[#EAECEF]">客群</h1>
    <button onclick="toggleSearch()" class="w-8 h-8 flex items-center justify-center">
      <i class="fa-solid fa-magnifying-glass text-[#848E9C] text-[16px]"></i>
    </button>
  </div>
  <!-- 搜索栏 -->
  <div id="search-bar" class="hidden bg-[#0B0E11] px-4 py-2 border-b border-[#2E3440]">
    <div class="flex items-center gap-2 bg-[#1E2329] rounded-xl px-3 py-2.5 border border-[#2E3440]">
      <i class="fa-solid fa-magnifying-glass text-[#474D57] text-[13px]"></i>
      <input id="search-input" type="text" placeholder="搜索 UID 或姓名"
        class="flex-1 bg-transparent text-[#EAECEF] text-[14px] outline-none placeholder-[#474D57]"
        oninput="onSearch(this.value)" />
      <button onclick="clearSearch()" id="clear-btn" class="text-[#474D57] text-[12px] hidden">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </div>
  <div id="search-results" class="hidden overflow-y-auto pb-[90px]" style="scrollbar-width:none;">
    <div class="px-4 pt-3 pb-1"><span class="text-[12px] text-[#848E9C]" id="search-hint">输入 UID 或姓名搜索</span></div>
    <div id="search-list" class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mt-2"></div>
  </div>
  <!-- 主内容 -->
  <div id="main-content">
    <!-- 三段胶囊 -->
    <div class="flex bg-[#1E2329] rounded-xl mx-4 mt-3 p-1 border border-[#2E3440]">
      <button onclick="switchSegment('high')" id="seg-high"
        class="flex-1 py-2 rounded-lg text-[13px] font-semibold bg-[#F0B90B] text-[#0B0E11]">高价值</button>
      <button onclick="switchSegment('develop')" id="seg-develop"
        class="flex-1 py-2 rounded-lg text-[13px] text-[#848E9C]">高潜</button>
      <button onclick="switchSegment('starred')" id="seg-starred"
        class="flex-1 py-2 rounded-lg text-[13px] text-[#848E9C] flex items-center justify-center gap-1">
        <i class="fa-solid fa-star text-[11px]"></i>收藏</button>
    </div>
    <!-- 二级 pills（高价值时显示）-->
    <div id="pills-row" class="flex gap-2 px-4 pt-3 pb-1 overflow-x-auto" style="scrollbar-width:none;">
      <button onclick="switchPill('all')" id="pill-all" class="pill-active rounded-full px-3 py-1.5 text-[12px] whitespace-nowrap">综合</button>
      <button onclick="switchPill('spot')" id="pill-spot" class="pill-inactive rounded-full px-3 py-1.5 text-[12px] whitespace-nowrap">现货活跃</button>
      <button onclick="switchPill('futures')" id="pill-futures" class="pill-inactive rounded-full px-3 py-1.5 text-[12px] whitespace-nowrap">合约贡献</button>
    </div>
    <!-- 统计行 -->
    <div id="stats-row" class="px-4 py-2">
      <span class="text-[11px] text-[#848E9C]">覆盖 <span class="text-[#EAECEF] font-semibold">{len(all_rows)}</span> 人 · 高价值 <span class="text-[#F0B90B] font-semibold">{len(hv)}</span> · 高潜 <span class="text-[#4DA6FF] font-semibold">{len(hp)}</span></span>
      <div class="hidden">
      </div>
    </div>
    <!-- 内容区 -->
    <div id="content-area" class="overflow-y-auto pb-[90px]" style="scrollbar-width:none;">
      <!-- 综合 -->
      <div id="panel-all">
        <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">全部客户 · 按综合净贡献 N90 降序 · 共{len(all_sorted)}人</p></div>
        <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mb-4">
'''
    for i, r in enumerate(all_sorted, 1):
        html += client_row_html(r, i, last=(i == len(all_sorted)))
    html += '''        </div>
      </div>
      <!-- 现货活跃 -->
      <div id="panel-spot" class="hidden">
'''
    html += f'        <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">按现货活跃天数排序 · 共{len(spot_sorted)}人</p></div>\n'
    html += '        <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mb-4">\n'
    for i, r in enumerate(spot_sorted, 1):
        html += client_row_html(r, i, last=(i == len(spot_sorted)))
    html += '        </div>\n      </div>\n'

    # 合约贡献
    html += '      <div id="panel-futures" class="hidden">\n'
    html += f'        <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">按双仓合约净贡献排序 · 共{len(fut_sorted)}人</p></div>\n'
    html += '        <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden mb-4">\n'
    for i, r in enumerate(fut_sorted, 1):
        html += client_row_html(r, i, last=(i == len(fut_sorted)))
    html += '        </div>\n      </div>\n'

    # 高潜
    html += '      <div id="panel-develop" class="hidden">\n'
    html += f'        <div class="px-4 pb-1"><p class="text-[11px] text-[#848E9C]">按机会缺口降序 · 理论贡献−实际贡献 · 共{len(hp_sorted)}人</p></div>\n'
    html += '        <div class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3140] overflow-hidden mb-4">\n'
    for i, r in enumerate(hp_sorted, 1):
        html += hp_row_clients(r, i, last=(i == len(hp_sorted)))
    html += '        </div>\n      </div>\n'

    # 收藏
    html += '''      <div id="panel-starred" class="hidden pb-4">
        <div class="px-4 pb-2"><p class="text-[11px] text-[#848E9C]">点击客户行右侧 ☆ 即可添加收藏</p></div>
        <div id="starred-list" class="mx-4 bg-[#1E2329] rounded-xl border border-[#2E3440] overflow-hidden"></div>
        <div id="starred-empty" class="flex flex-col items-center justify-center py-16 hidden">
          <i class="fa-regular fa-star text-[#474D57] text-[48px] mb-4"></i>
          <p class="text-[14px] text-[#848E9C]">暂无收藏客户</p>
        </div>
      </div>
    </div>
  </div>
'''

    # 构建搜索数据
    search_data = [{
        'uid': r['uid'], 'name': r['name'],
        'n90': fmt_n(r['N90']), 'f90': fmt_f(r['F90']),
        'label': r['label'], 'recommend': recommend_short(r['recommend']),
        'href': client_detail_href(r['uid'])
    } for r in all_sorted]

    import json
    html += f'''
  <!-- 底部 Tab -->
  <div class="fixed-bar bg-[#0B0E11] border-t border-[#2E3440] z-20">
    <div class="flex items-center justify-around h-[56px]">
      <a href="#" onclick="goHome()" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-house text-[#848E9C] text-[18px]"></i>
        <span class="text-[10px] text-[#848E9C]">首页</span>
      </a>
      <a href="clients.html" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-users text-[#F0B90B] text-[18px]"></i>
        <span class="text-[10px] text-[#F0B90B] font-medium">客群</span>
      </a>
      <a href="events.html" class="flex flex-col items-center gap-0.5">
        <div class="relative">
          <i class="fa-solid fa-bell text-[#848E9C] text-[18px]"></i>
          <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-[#F6465D]"></span>
        </div>
        <span class="text-[10px] text-[#848E9C]">事件</span>
      </a>
      <a href="profile.html" class="flex flex-col items-center gap-0.5">
        <i class="fa-solid fa-circle-user text-[#848E9C] text-[18px]"></i>
        <span class="text-[10px] text-[#848E9C]">我的</span>
      </a>
    </div>
    <div class="h-[34px]"></div>
  </div>
</div>
<script>
  const SEARCH_DATA = {json.dumps(search_data, ensure_ascii=False)};
  const STAR_KEY = 'starred_clients';
  let starred = new Set(JSON.parse(localStorage.getItem(STAR_KEY) || '[]'));

  function saveStars() {{ localStorage.setItem(STAR_KEY, JSON.stringify([...starred])); }}
  function toggleStar(uid) {{
    starred.has(uid) ? starred.delete(uid) : starred.add(uid);
    saveStars();
    const el = document.getElementById('star-' + uid);
    if(el) el.className = starred.has(uid) ? 'fa-solid fa-star text-[#F0B90B] text-[15px]' : 'fa-regular fa-star text-[#474D57] text-[15px]';
    if(currentSeg === 'starred') renderStarred();
  }}
  function renderStarred() {{
    const list = document.getElementById('starred-list');
    const empty = document.getElementById('starred-empty');
    const items = SEARCH_DATA.filter(c => starred.has(c.uid));
    if(!items.length) {{ list.innerHTML=''; list.classList.add('hidden'); empty.classList.remove('hidden'); return; }}
    empty.classList.add('hidden'); list.classList.remove('hidden');
    list.innerHTML = items.map((c,i) => `
      <div onclick="location.href='${{c.href}}'" class="flex items-center px-4 py-3 ${{i<items.length-1?'border-b border-[#2E3440]':''}} active:bg-[#2B3139] cursor-pointer">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5 mb-0.5">
            <span class="text-[14px] font-semibold text-[#EAECEF]">${{c.name}}</span>
            <span class="text-[11px] text-[#474D57]">${{c.uid}}</span>
            <span class="text-[13px] font-bold text-[#F8D33A]">${{c.n90}}</span>
          </div>
          <p class="text-[11px] text-[#848E9C] truncate">${{c.label}} · 推荐：${{c.recommend}}</p>
        </div>
        <button onclick="event.stopPropagation();toggleStar('${{c.uid}}')" class="ml-2 w-8 h-8 flex items-center justify-center">
          <i class="fa-solid fa-star text-[#F0B90B] text-[15px]"></i>
        </button>
      </div>`).join('');
  }}

  let currentSeg = 'all';
  function switchSegment(seg) {{
    currentSeg = seg;
    const isHigh = ['all','spot','futures'].includes(seg);
    document.getElementById('pills-row').classList.toggle('hidden', !isHigh);
    document.getElementById('stats-row').classList.toggle('hidden', seg === 'starred');
    ['all','spot','futures','develop','starred'].forEach(p => {{
      document.getElementById('panel-' + p).classList.add('hidden');
    }});
    if(isHigh) document.getElementById('panel-' + seg).classList.remove('hidden');
    else document.getElementById('panel-' + seg).classList.remove('hidden');
    ['high','develop','starred'].forEach(s => {{
      const active = (isHigh && s==='high') || s===seg;
      const btn = document.getElementById('seg-' + s);
      btn.className = active
        ? 'flex-1 py-2 rounded-lg text-[13px] font-semibold bg-[#F0B90B] text-[#0B0E11]'
        : 'flex-1 py-2 rounded-lg text-[13px] text-[#848E9C] flex items-center justify-center gap-1';
      if(s==='starred') btn.innerHTML = '<i class="fa-solid fa-star text-[11px]"></i>收藏';
    }});
    if(seg === 'starred') renderStarred();
  }}
  function switchPill(p) {{
    ['all','spot','futures'].forEach(id => {{
      document.getElementById('pill-' + id).className = id===p
        ? 'pill-active rounded-full px-3 py-1.5 text-[12px] whitespace-nowrap'
        : 'pill-inactive rounded-full px-3 py-1.5 text-[12px] whitespace-nowrap';
      document.getElementById('panel-' + id).classList.toggle('hidden', id!==p);
    }});
    currentSeg = p;
  }}
  function toggleSearch() {{
    const bar = document.getElementById('search-bar');
    const isOpen = !bar.classList.contains('hidden');
    if(isOpen) {{
      bar.classList.add('hidden');
      document.getElementById('search-results').classList.add('hidden');
      document.getElementById('main-content').classList.remove('hidden');
      document.getElementById('search-input').value = '';
    }} else {{
      bar.classList.remove('hidden');
      setTimeout(() => document.getElementById('search-input').focus(), 50);
    }}
  }}
  function onSearch(q) {{
    const results = document.getElementById('search-results');
    const main = document.getElementById('main-content');
    document.getElementById('clear-btn').classList.toggle('hidden', !q);
    if(!q) {{ results.classList.add('hidden'); main.classList.remove('hidden'); return; }}
    results.classList.remove('hidden'); main.classList.add('hidden');
    const matched = SEARCH_DATA.filter(c => c.name.includes(q) || c.uid.includes(q));
    document.getElementById('search-hint').textContent = matched.length ? `找到 ${{matched.length}} 个客户` : '无匹配结果';
    const list = document.getElementById('search-list');
    if(!matched.length) {{ list.innerHTML = `<div class="px-4 py-6 text-center text-[13px] text-[#474D57]">未找到 UID 或姓名包含"${{q}}"的客户</div>`; return; }}
    list.innerHTML = matched.map((c,i) => `
      <div onclick="location.href='${{c.href}}'" class="flex items-center px-4 py-3 ${{i<matched.length-1?'border-b border-[#2E3440]':''}} active:bg-[#2B3139] cursor-pointer">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5 mb-0.5">
            <span class="text-[14px] font-semibold text-[#EAECEF]">${{c.name}}</span>
            <span class="text-[11px] text-[#474D57]">${{c.uid}}</span>
            <span class="text-[13px] font-bold text-[#F8D33A]">${{c.n90}}</span>
          </div>
          <p class="text-[11px] text-[#848E9C] truncate">${{c.label}}</p>
        </div>
      </div>`).join('');
  }}
  function clearSearch() {{ document.getElementById('search-input').value=''; onSearch(''); document.getElementById('search-input').focus(); }}
  function goHome() {{ location.href = 'home-' + (sessionStorage.getItem('homeVersion') || 'a') + '.html'; }}

  const initTab = new URLSearchParams(location.search).get('tab') || 'all';
  if(initTab === 'develop') switchSegment('develop');
  else switchSegment('all');
</script>
</body>
</html>
'''
    return html

# ─── 主流程 ────────────────────────────────────────────────────────
def main():
    print('读取模拟数据...')
    rows = load()
    runtime_data = build_mock_data(rows)

    hv = sorted([r for r in rows if r['label'] == '高价值客户'],
                key=lambda x: x['N90'], reverse=True)
    hp = sorted([r for r in rows if r['label'] == '高潜客户'],
                key=lambda x: x['opportunity_gap'], reverse=True)

    print(f'高价值: {len(hv)}人  高潜: {len(hp)}人  总计: {len(rows)}人')

    runtime_path = f'{PROTO}/mock-data.js'
    with open(runtime_path, 'w', encoding='utf-8') as f:
        f.write(serialize_mock_data_js(runtime_data))
    print(f'  写入 mock-data.js  ({os.path.getsize(runtime_path)//1024}KB)')

    pages = {
        'home-a.html': gen_home_a(hv, hp),
        'home-b.html': gen_home_b(hv, hp, rows),
        'home-c.html': gen_home_c(hv, hp),
        'clients.html': gen_clients(rows, hv, hp),
    }

    for fname, html in pages.items():
        path = f'{PROTO}/{fname}'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        size = os.path.getsize(path)
        print(f'  写入 {fname}  ({size//1024}KB)')

    print('完成。')

if __name__ == '__main__':
    main()
