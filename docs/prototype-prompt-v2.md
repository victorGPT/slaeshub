> 将此 prompt 完整提供给 AI 工具生成原型代码

---

# Role

You are a world-class UI/UX engineer and frontend developer, specializing in crypto-finance B2B mobile applications. You excel at building pixel-perfect dark-theme interfaces with Tailwind CSS, implementing complex data hierarchies, and creating interactive multi-state prototypes that feel native on mobile.

---

# Task

Create a high-fidelity multi-page HTML prototype for **Sales Hub** — a BD (Business Development) workstation for a crypto exchange. BD reps use this to monitor high-value clients, act on system-generated events, and record follow-ups.

Design style: **custom dark crypto-finance** (inspired by Binance dark mode). Core keywords: **暗色专业、金色点睛、数据密集、层次清晰、移动优先**.

Build 7 independent HTML pages + 1 index entry:

| File | Page |
|------|------|
| `index.html` | 移动端导航入口，选择进入版本 A / B / C |
| `home-a.html` | 首页 版本A（卡片·综合单视图，顶部两Tab） |
| `home-b.html` | 首页 版本B（卡片·综合/现货/合约三子Tab，顶部两Tab） |
| `home-c.html` | 首页 版本C（两行列表·高密度，顶部两Tab） |
| `clients.html` | 客户列表 |
| `client-detail.html` | 客户详情（360° 数据面板） |
| `event-thread.html` | 事件线程（四态（未开始/跟进中/已结束/忽略）任务 + AI 建议） |
| `events.html` | 事件中心 |

---

# Tech Stack

- **Output**: Each page is an independent `.html` file. `index.html` uses `<iframe>` to show all pages with a page-selector dropdown.
- **CSS Framework**: Tailwind CSS via CDN `<script src="https://cdn.tailwindcss.com"></script>`
- **Icons**: FontAwesome 6 Free via CDN `<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">`
- **Device Simulation**: 393px width (iPhone 15 Pro), centered on desktop with `max-w-[393px] mx-auto`. Include simulated iOS status bar (44px, shows 9:41, signal, battery) and bottom safe area (34px).
- **Images**: Use `https://i.pravatar.cc/40?u={name}` for client avatars (40px circles).
- **JavaScript**: Vanilla JS only, inline `<script>` per page. Used for: AB version toggle, task state transitions, tab switching.
- **No build tools**, no external frameworks, no React. Pure HTML + Tailwind + vanilla JS.

---

# Visual Design Requirements

## 1. Color Palette

```
Background Colors:
- Page Background:    #0B0E11  (deepest dark, body bg)
- Card Background:    #1E2329  (elevated surface)
- Card Hover/Active:  #2B3139  (slightly lighter card)
- Input / Divider:    #2E3440  (borders, separators)

Primary Colors:
- Gold (Primary):     #F0B90B  (CTA buttons, active tabs, key values, rank numbers)
- Gold Dim:           #B8860B  (secondary gold, disabled gold state)
- Gold Text:          #F8D33A  (large metric numbers)

Status Colors:
- Risk Red:           #F6465D  (losses, alerts, risk signal)
- Risk Red BG:        #2D1B1E  (red signal card background)
- Opportunity Yellow: #F0B90B  (opportunity signal, same as gold)
- Stable Gray:        #848E9C  (stable/neutral signal)
- Success Green:      #0ECB81  (profit, positive, completed)
- Success Green BG:   #0D2620  (green signal card background)

Text Colors:
- Primary Text:       #EAECEF  (headings, key labels)
- Secondary Text:     #848E9C  (subtitles, meta info)
- Disabled Text:      #474D57  (inactive items)
- Link / Highlight:   #F0B90B  (clickable gold text)

Tag Colors:
- System Tag BG:      #2C2E38  (auto-generated tags)
- System Tag Text:    #C0C6D1  (auto tag text)
- BD Tag BG:          #1A2634  (manual BD tags, blue tint)
- BD Tag Text:        #5B9BD5  (manual tag text)
- Top10 Tag BG:       #2D2010  (ranking tags, gold tint)
- Top10 Tag Text:     #F0B90B  (ranking tag text)

Task State Colors:
- Pending BG:         #2D1B00  / Text: #F0B90B   (未开始)
- In-Progress BG:     #0D1F2D  / Text: #4DA6FF   (跟进中)
- Completed BG:       #0D2620  / Text: #0ECB81   (已结束)
- Ignored BG:         #1A1A1A  / Text: #848E9C   (忽略)
```

## 2. UI Style Characteristics

**Cards:**
- Background: `#1E2329`
- Border Radius: `12px` (`rounded-xl`)
- Border: `1px solid #2E3440`
- No drop shadow (flat dark design)
- Padding: `16px`
- Margin between cards: `8px`

**Primary Button (Gold):**
- Background: `#F0B90B`, Text: `#0B0E11` (black), Height: `48px`
- Border Radius: `8px` (`rounded-lg`)
- Font: `15px font-semibold`
- Active: `active:opacity-80`

**Secondary Button (Outline):**
- Border: `1px solid #F0B90B`, Text: `#F0B90B`, Background: transparent
- Same dimensions as primary

**Ghost Button:**
- Background: `#2B3139`, Text: `#EAECEF`, Height: `36px`, Radius: `6px`

**Tags / Badges (pill shape):**
- Padding: `2px 8px`, Border Radius: `999px` (`rounded-full`)
- Font: `11px`
- Three visual variants: system (gray), BD-manual (blue), ranking (gold)

**Icons:**
- Use FontAwesome 6 icons throughout
- Icon size: `14px` (inline), `18px` (standalone), `22px` (tab bar)
- Icon color: `#848E9C` default, `#F0B90B` active/primary

**List Items:**
- Height: `64px` minimum (two-line), `52px` (single-line)
- Left: avatar (40px circle) or icon (32px in colored container)
- Separator: `1px solid #2E3440`, no inset

**Signal Dots:**
- 🔴 Risk: `w-2 h-2 rounded-full bg-[#F6465D]`
- 🟡 Opportunity: `w-2 h-2 rounded-full bg-[#F0B90B]`
- ⚪ Stable: `w-2 h-2 rounded-full bg-[#848E9C]`

## 3. Layout Structure (393px mobile)

**Top Navigation Bar (52px):**
- Background: `#0B0E11` with `border-b border-[#2E3440]`
- Title: centered, `16px font-semibold`, color `#EAECEF`
- Left: back arrow `<i class="fa-solid fa-chevron-left">` or hamburger
- Right: icon buttons (bell, filter, etc.) in `#848E9C`
- `sticky top-0 z-20`

**Status Bar (simulated, 44px):**
- Background: `#0B0E11`
- Left: `9:41` in `12px #EAECEF`
- Right: signal bars + wifi + battery in `#EAECEF`

**Bottom Tab Bar (56px + 34px safe area):**
- Background: `#0B0E11` with `border-t border-[#2E3440]`
- `fixed bottom-0 w-full`
- 4 tabs: **首页** / **客群** / **事件** / **我的**
- Active: icon + text both `#F0B90B`
- Inactive: icon + text both `#848E9C`
- Badge: red dot `8px` circle on event tab when there are unread items

**Scrollable Content Area:**
- `overflow-y-auto` between sticky header and fixed footer
- Padding bottom: `90px` (to clear tab bar)
- Padding top: `0` (header is sticky)

## 4. 首页三版本设计说明

首页拆分为三个独立文件，各版本无页内切换按钮，通过 `index.html` 入口分别进入。版本选择写入 `sessionStorage('homeVersion')`，其他页面底部 Tab 点"首页"时读取并跳转对应版本，保持一致性。

| 版本 | 文件 | 榜单形态 | 核心差异 |
|------|------|---------|---------|
| A | `home-a.html` | 卡片 · 综合单视图 | 极简聚焦，信息完整 |
| B | `home-b.html` | 卡片 · 综合/现货/合约三子Tab | 多维分层，按业务线切换 |
| C | `home-c.html` | **两行列表** · 综合单视图 | 高密度，一屏可见7条 |

首页结构（三版本一致）：顶部两个 Tab [高价值客户] [高潜力客户]，各 Tab 底部有"查看全部"入口链到 clients.html。今日行动已移除。

**版本 C 列表格式说明（高密度）：**
- 单行高度约 52px（卡片约 100px），一屏可见约 7 个客户
- 去掉头像、信号 dot（信号 dot 移至客户详情页）
- 行1：`#排名 姓名 · +手续费贡献 · 周环比 · [Tag]`
- 行2：AI建议文字（金色，truncate，末尾 →）
- 榜单内所有行共用一个圆角容器，行间细分隔线

---

# Page-by-Page Specifications

## Page 1: home-a.html / home-b.html / home-c.html — 首页

> 三个版本共用相同的数据和结构，差异仅在**榜单形态**和**今日行动分组**，见第4节说明。

### 核心设计原则

- **首要指标是手续费贡献**，交易量本身不作为榜单核心展示字段
- **信号 dot 不在榜单/列表中展示**，移至客户详情页
- 周环比（`▲/▼ +X%`）展示贡献趋势，帮助 BD 快速判断是否点入

### Upper Half: 客群榜单 (Client Ranking Lists)

#### 高价值客户榜单

**Section Header:**
```
高价值客户        近30天手续费贡献排行
```

**版本 A / C（综合单视图）:**
Show a single ranked list of top clients by combined fee contribution (近30天综合净贡献).

Rank cards (3 visible, horizontal scroll hint):

| Rank | Client | 综合净贡献 | 资沉 | Signal | Tag |
|------|--------|-----------|------|--------|-----|
| #1 | 王伟明 | +$284,320 | $12.4M | 🔴 风险 | 合约强 贡献Top5 |
| #2 | 陈浩然 | +$176,540 | $8.9M | ⚪ 稳定 | 高频交易·低资沉 |
| #3 | 张晓峰 | +$143,200 | $22.1M | 🟡 机会 | 贡献Top10 资沉Top20 |
| #4 | 刘思远 | +$98,760 | $5.3M | ⚪ 稳定 | 现货强 |
| #5 | 孙嘉琪 | +$87,430 | $18.7M | 🟡 机会 | 合约强 期货亏损 |

AI建议 (one line per card):
- 王伟明: "近3日出金$2.1M，建议今日致电确认资产留存意向"
- 陈浩然: "高频合约手但资沉极低，留存风险高，建议询问理财意向"
- 张晓峰: "资沉大但贡献释放不足，是本周重点开发对象"

**版本 B（综合 + 现货 + 合约三视图，卡片形态）:**
Add a sub-tab switcher inside the section:
```
[综合] [现货] [合约]
```
- 综合: same as A
- 现货高价值 (近30天现货手续费净贡献):

| Rank | Client | 现货手续费 | 资沉 | Signal |
|------|--------|-----------|------|--------|
| #1 | 林小雅 | +$52,800 | $4.2M | ⚪ 稳定 |
| #2 | 赵宇航 | +$41,300 | $6.8M | 🟡 机会 |
| #3 | 钱多多 | +$38,900 | $3.1M | ⚪ 稳定 |

- 合约高价值 (双仓+超杠+Mini之和):

| Rank | Client | 合约净贡献 | 资沉 | Signal |
|------|--------|-----------|------|--------|
| #1 | 王伟明 | +$241,200 | $12.4M | 🔴 风险 |
| #2 | 陈浩然 | +$159,700 | $8.9M | ⚪ 稳定 |
| #3 | 吴建国 | +$112,500 | $31.2M | 🟡 机会 |

**版本 A / B 客户卡片结构：**
```
┌─────────────────────────────────────────┐
│ #1  [Avatar] 王伟明                      │
│              [合约强] [贡献Top5]          │
│ 综合净贡献   +$284,320 ▲12% 周环比        │
│ 资金沉淀     $12.4M                      │
│ AI建议: 近3日出金$2.1M，建议今日致电...   │
└─────────────────────────────────────────┘
```
- 信号 dot 不在卡片展示（已移至客户详情页）
- Card width: full width minus 32px margins
- Avatar: 40px circle, `border-2 border-[#F0B90B]` for top-3
- Rank number: `#1` in `#F0B90B` font-bold 18px, `#2` `#3` in `#EAECEF`, rest in `#848E9C`
- Metric label: `11px #848E9C`
- Metric value: `20px font-bold #F8D33A`
- 周环比: `12px`, green if positive (`▲ +12%`), red if negative (`▼ -5%`)
- AI建议: `12px #848E9C` italic, truncated to 1 line with `...`

**版本 C 列表行结构：**
```
#1  王伟明  +$284K  ▲12%  [合约强] [贡献Top5]
    近3日出金$2.1M，建议今日致电确认资产留存意向 →
```
- 无头像，无信号 dot
- 行1: 排名 + 姓名 + 贡献值 + 周环比 + Tags，全部内联排列，`flex-wrap`
- 行2: AI建议，`11px #F0B90B`，truncate，末尾 `→`
- 单行高度约 52px，所有行共用一个 `bg-[#1E2329] rounded-xl` 容器，行间 `border-b border-[#2E3440]`
- 一屏可见约 7 个客户（卡片版约 3 个）

#### 高潜力客户榜单

Section title: `高潜力客户` + subtitle: `近90天日均资沉排行 · 资金利用率偏低`

| Rank | Client | 日均资沉 | 资金利用率 | Signal | Tag |
|------|--------|---------|-----------|--------|-----|
| #1 | 吴建国 | $31.2M | 2.1% | 🟡 机会 | 资沉Top5 纯理财 |
| #2 | 郑梦琪 | $19.8M | 3.4% | 🟡 机会 | 资沉Top15 持续盈利 |
| #3 | 周大鹏 | $15.6M | 1.8% | 🟡 机会 | 资沉Top20 理财为主 |

AI建议:
- 吴建国: "$31M资沉几乎全在理财，转化合约潜力极大，建议邀约体验合约账户"
- 郑梦琪: "近期有盈利，情绪正面，适合推介新产品"
- 周大鹏: "连续90天资沉稳定但零合约，优先级最高的开发目标"

**高潜力卡片结构:**
```
┌─────────────────────────────────────────┐
│ #1  [Avatar] 吴建国          🟡          │
│              [资沉Top5] [纯理财]          │
│ 日均资沉     $31.2M                      │
│ 资金利用率   2.1%  ████░░░░░░ (低)       │
│ AI建议: $31M资沉几乎全在理财，转化合约...  │
└─────────────────────────────────────────┘
```
- 资金利用率 progress bar: thin bar (4px height), filled portion in `#F0B90B`, background `#2E3440`
- Label "低" in `#F6465D`, "中" in `#F0B90B`, "高" in `#0ECB81`

### 今日行动已移除

**决策：首页不再包含今日行动 section。**

理由：今日行动本质上是事件中心（events.html）按"未开始"筛选的子集，在首页重复展示造成冗余。职责拆分：
- **首页 = 看人**（高价值 / 高潜力 两个 Tab 榜单）
- **事件中心 = 看事**（全量事件 + 状态筛选，底部 Tab 红点 badge 提示未开始数）

---

## Page 2: clients.html — 客户列表

**Top Nav:** `客群` title, right: search icon `<i class="fa-solid fa-magnifying-glass">`

**Filter Bar (horizontal scroll, 36px height):**
```
[全部] [高价值] [高潜力] [合约强] [高资沉] [有未开始事件]
```
- Active filter pill: `bg-[#F0B90B] text-[#0B0E11]`
- Inactive: `bg-[#1E2329] text-[#848E9C] border border-[#2E3440]`

**Stats Summary Row (3 metrics):**
```
┌──────────┬──────────┬──────────┐
│ 覆盖客户  │ 高价值    │ 高潜力   │
│   38     │   12     │   8      │
└──────────┴──────────┴──────────┘
```
- Each cell: `bg-[#1E2329]`, number `24px font-bold #F8D33A`, label `11px #848E9C`

**Client List:**

Each client row:
```
┌──────────────────────────────────────────┐
│ [Avatar] 王伟明              🔴  >        │
│          [合约强] [贡献Top5]              │
│          贡献 $284K · 资沉 $12.4M        │
└──────────────────────────────────────────┘
```
- Height: `72px`
- Avatar: 44px, with colored ring: gold for high-value, blue for under-developed
- Name: `15px font-semibold #EAECEF`
- Tags: up to 3 tags, pill style, `11px`
- Metrics: `12px #848E9C`
- Signal dot: right-aligned
- Tap row → navigate to `client-detail.html`

Mock client list (10 clients):
1. 王伟明 — [合约强][贡献Top5] — 贡献$284K · 资沉$12.4M — 🔴
2. 陈浩然 — [高频交易·低资沉][贡献Top10] — 贡献$177K · 资沉$8.9M — ⚪
3. 张晓峰 — [贡献Top10][资沉Top20] — 贡献$143K · 资沉$22.1M — 🟡
4. 吴建国 — [资沉Top5][纯理财] — 贡献$18K · 资沉$31.2M — 🟡
5. 郑梦琪 — [资沉Top15][持续盈利] — 贡献$54K · 资沉$19.8M — 🟡
6. 周大鹏 — [资沉Top20][理财为主] — 贡献$22K · 资沉$15.6M — 🟡
7. 刘思远 — [现货强] — 贡献$99K · 资沉$5.3M — ⚪
8. 孙嘉琪 — [合约强][期货亏损] — 贡献$87K · 资沉$18.7M — 🟡
9. 林小雅 — [现货强] — 贡献$53K · 资沉$4.2M — ⚪
10. 赵宇航 — [持续盈利] — 贡献$41K · 资沉$6.8M — 🟡

---

## Page 3: client-detail.html — 客户详情

**Top Nav:** Back arrow + `王伟明` title + right: `<i class="fa-solid fa-ellipsis">` menu

**Client Header Card:**
```
┌─────────────────────────────────────────┐
│ [Avatar 64px]  王伟明                   │
│                UID: 10023841             │
│                BD: 李明远 · 接入 2024.06 │
│ [合约强] [贡献Top5] [高频交易·低资沉]    │
│ (system tags above, auto-generated)      │
│ [脾气不好] [偏好短线] [英文沟通]          │
│ (BD manual tags, blue tint)              │
└─────────────────────────────────────────┘
```
- System tags: `bg-[#2C2E38] text-[#C0C6D1]` + lock icon `🔒` tiny
- BD tags: `bg-[#1A2634] text-[#5B9BD5]` + pencil icon for editable
- "+ 添加标签" button: dashed border `border-dashed border-[#2E3440]`, text `#848E9C`

**Core Metrics Grid (2×3):**
```
┌─────────────┬─────────────┐
│ 集团净贡献   │ 资金沉淀     │
│ +$284,320   │ $12.4M      │
│ ▲ +12% 周环比  │ ▼ -8% 周环比  │
├─────────────┼─────────────┤
│ 资金利用率   │ 近30天交易量  │
│  78.3%      │ $3.2M       │
│ 高 ████████ │             │
├─────────────┼─────────────┤
│ 合约净贡献   │ 本月盈亏      │
│ +$241,200   │ -$45,000    │
│             │ 亏损中 🔴    │
└─────────────┴─────────────┘
```
- Each cell: `bg-[#1E2329] rounded-xl p-4`
- Metric label: `11px #848E9C`
- Metric value: `22px font-bold #F8D33A` (positive in `#0ECB81`, negative in `#F6465D`)
- 周环比: `12px`, colored per direction

**业务线拆分 (collapsible, default expanded):**
Section title: `业务线明细 · 近30天`

| 业务线 | 贡献 | 占比 |
|--------|------|------|
| 双仓合约 | +$198,400 | 69.8% |
| 超级杠杆 | +$42,800 | 15.1% |
| Mini合约 | — | — |
| 金融卡 | +$12,300 | 4.3% |
| 云算力 | +$8,200 | 2.9% |
| 理财利息 | -$18,500 | -6.5% |
| 返佣支出 | -$8,380 | -3.0% |

Display as a horizontal bar chart per row: label + thin bar (`bg-[#F0B90B]`) + value

**BD 备注 (textarea):**
```
┌─────────────────────────────────────────┐
│ BD 备注                        [编辑]   │
│ 王总比较强势，沟通时避免推荐复杂产品。     │
│ 偏好短线合约，每周五结账。                │
│ 上次见面 2026-03-15，送了礼品券。         │
└─────────────────────────────────────────┘
```
- Background: `#1E2329`, text `14px #EAECEF`, border `#2E3440`

**最近事件 (last 3):**
Section title: `最近事件`
Compact event rows (52px each):
1. 🔴 大额出金预警 — $2.1M — 10分钟前 — `未开始` badge → tap to event-thread.html
2. 🟡 本月盈利超阈值 — 盈利$82K — 3小时前 — `未开始` badge
3. ⚪ 首次合约体验邀约 — BD主动记录 — 3天前 — `已结束` badge

**跟进记录时间线 (last 3 entries):**
Section title: `跟进记录`
Timeline style (left vertical line in `#2E3440`):
- 2026-03-25: "致电约15分钟，确认资产不会继续出金，暂时稳住。" — 李明远
- 2026-03-18: "微信发送了黄金合约活动资料，王总表示感兴趣。" — 李明远
- 2026-03-10: "线下会面，送了定制礼品，氛围不错。" — 李明远

`+ 添加跟进记录` button: full-width ghost button at bottom

---

## Page 4: event-thread.html — 事件线程

**Top Nav:** Back arrow + event type as title (e.g., `大额出金预警`) + signal dot

**Event Header Card:**
```
┌─────────────────────────────────────────┐
│ 🔴 大额出金预警                           │
│ 触发时间: 2026-03-28 09:32              │
│ [Avatar 32px] 王伟明 · UID 10023841    │
│                                         │
│ 出金金额:    $2,100,000                  │
│ 出金渠道:    USDT TRC-20                │
│ 近7日出金:   $3.8M (较8周均值 ▲240%)         │
│ 当前资沉:    $12.4M                      │
└─────────────────────────────────────────┘
```
- Data fields: label `12px #848E9C`, value `15px #EAECEF`
- Key value (出金金额): `22px font-bold #F6465D` (red for risk)
- Trigger rule note: `12px #474D57 italic` "规则：单日出金 > $500K 触发"

**四态（未开始/跟进中/已结束/忽略）状态切换 (task state machine):**
Current state shown as prominent badge:
```
         [未开始]  →  [开始跟进]  →  [标记完成] or [忽略]
```
State transition bar at top of action area:
- Current state: large colored pill badge
- Action buttons change based on current state:
  - 未开始: show `[开始跟进]` (primary gold) + `[忽略]` (ghost)
  - 跟进中: show `[标记完成]` (green) + `[添加跟进记录]` (ghost)
  - 已结束: show read-only "已结束 · 2026-03-28 11:45" + `[查看记录]`
  - 忽略: show read-only "忽略" + optional reason + `[重新打开]`

Implement state transitions with JS: clicking buttons updates state badge and action buttons.

**AI 行动建议卡片:**
```
┌─────────────────────────────────────────┐
│ 🤖 AI 行动建议          [重新生成]       │
│─────────────────────────────────────────│
│ 核心判断：王伟明近期出金行为异常，7日累计  │
│ 出金$3.8M，建议今日优先处理。             │
│                                         │
│ 建议行动：                               │
│ 1. 致电了解出金原因（外部流动性需求还是   │
│    平台体验问题）                         │
│ 2. 如是外部原因，询问是否需要资金支持     │
│ 3. 视情况提供定制化理财/合约活动挽留      │
└─────────────────────────────────────────┘
```
- Card: `bg-[#1A2420] border border-[#0ECB81]/30` (subtle green tint for AI card)
- Title: `14px font-semibold #0ECB81`
- Body: `14px #EAECEF`
- "重新生成" button: ghost, `12px #848E9C`

**AI 话术模板（可编辑）:**
```
┌─────────────────────────────────────────┐
│ 📝 话术模板              [编辑] [复制]   │
│─────────────────────────────────────────│
│ 王总，您好！注意到您近期有大额资产调动，  │
│ 不知道是否有什么我可以协助的？我们最近刚  │
│ 推出了一个专属的定期理财产品，年化约      │
│ 6.5%，非常适合短期资产停泊，您有兴趣了解  │
│ 一下吗？                                 │
└─────────────────────────────────────────┘
```
- Card: `bg-[#1E2329]`
- When "编辑" clicked: textarea becomes editable (`contenteditable` or `<textarea>`)
- "复制" button copies text to clipboard (JS)

**跟进记录 (inline thread):**
Section title: `跟进记录`
Timeline entry input:
- Textarea placeholder: "记录本次跟进内容..."
- Submit button: `[记录]` primary gold
- Existing entries shown in timeline above input (same style as client-detail)

---

## Page 5: events.html — 事件中心

**Top Nav:** `事件中心` title + right: filter icon + unread count badge

**State Filter Tabs (horizontal, full-width):**
```
[全部 12] [未开始 3] [跟进中 2] [已结束 5] [忽略 2]
```
- Active: `border-b-2 border-[#F0B90B] text-[#F0B90B]`
- Inactive: `text-[#848E9C]`

**Event Type Filter (horizontal scroll pills, 32px):**
```
[全部] [出金预警] [爆仓] [盈利] [充值] [人工]
```

**Event List:**

Full event card (72px height):
```
┌──────────────────────────────────────────┐
│ [Icon] 大额出金预警    [未开始] ·10分钟前 │
│        王伟明 · $2.1M 出金               │
│        建议：致电确认留存意向 >           │
└──────────────────────────────────────────┘
```
- Left icon container: 40px, `rounded-xl`, color matches signal
- Event type: `14px font-semibold #EAECEF`
- State badge: pill, right-aligned
- Time: `11px #474D57`
- Client + detail: `12px #848E9C`
- AI建议 preview: `12px #F0B90B`
- Tap row → navigate to `event-thread.html`

Mock event list (12 events, various states):
1. 王伟明 — 大额出金预警 — $2.1M — 🔴 未开始 — 10分钟前
2. 吴建国 — 首次合约充值 — $500K — 🟡 未开始 — 1小时前
3. 郑梦琪 — 本月盈利超阈值 — 盈利$82K — 🟡 未开始 — 3小时前
4. 陈浩然 — 大额爆仓警告 — 爆仓$340K — 🔴 跟进中 — 昨天
5. 张晓峰 — 持续提现提醒 — 累计$4.3M — 🟡 跟进中 — 昨天
6. 孙嘉琪 — 客户大额亏损 — 亏损$180K — 🔴 已结束 — 3天前
7. 刘思远 — 账户长期未登录 — 45天未登录 — ⚪ 已结束 — 4天前
8. 周大鹏 — 理财到期未续 — $3M到期 — 🟡 已结束 — 5天前
9. 赵宇航 — 邀约活动参与 — VIP活动邀约 — ⚪ 忽略 — 6天前
10. 林小雅 — 手续费优惠到期 — 下周到期 — ⚪ 已结束 — 1周前
11. 吴建国 — 资产配置建议 — 理财转合约 — 🟡 已结束 — 1周前
12. 王伟明 — 节日问候提醒 — 清明节前 — ⚪ 忽略 — 2周前

**Empty State (when filter returns 0):**
```
<i class="fa-regular fa-bell-slash text-[#474D57] text-5xl">
暂无相关事件
```

---

## Page 6: index.html — 入口导航

移动端原生导航页（宽度同样锁定 393px），包含：
- 三个版本入口卡片（A / B / C），各附说明文字和进入按钮
- 其他共用页面快捷入口（客户列表、客户详情、事件中心、事件线程）
- 无 iframe，点击直接跳转对应页面

---

# Implementation Details

- 宽度死锁：`html, body { width: 393px !important; margin: 0 auto; }`，`html { background: #000; }`，桌面两侧黑色填充
- Scrollable content: `overflow-y-auto` in a flex column layout between sticky header and fixed footer
- All bottom tab bars: `.fixed-bar { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 393px; }`
- 版本持久化：各 home 页写入 `sessionStorage('homeVersion', 'a'/'b'/'c')`；clients / events 页底部首页 tab 用 `goHome()` 读取并跳转
- Tailwind custom config: extend colors with all brand tokens (see config below)
- Typography: `font-family: 'PingFang SC', 'Helvetica Neue', sans-serif` via inline style on `<body>`
- Touch targets: all interactive elements minimum `44px × 44px`
- Scrollbars: `style="scrollbar-width: none"` or `::-webkit-scrollbar { display: none }`
- Number formatting: use `$` prefix, `K`/`M` suffix for large numbers (e.g., `$2.1M`, `$284K`)
- 周环比: `▲` for positive (green `#0ECB81`), `▼` for negative (red `#F6465D`)
- Progress bars: `h-1 rounded-full bg-[#2E3440]` container, inner `bg-[#F0B90B]` width set via inline style %
- 版本 A/B/C 为独立 HTML 文件，无页内 AB toggle 按钮
- State transitions in event-thread.html: JS updates className of state badge and swaps action buttons innerHTML
- All text must be in **Chinese** (Simplified)

---

# Tailwind Config

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'hub-bg':        '#0B0E11',
        'hub-card':      '#1E2329',
        'hub-card-hover':'#2B3139',
        'hub-border':    '#2E3440',
        'hub-gold':      '#F0B90B',
        'hub-gold-dim':  '#B8860B',
        'hub-gold-text': '#F8D33A',
        'hub-red':       '#F6465D',
        'hub-green':     '#0ECB81',
        'hub-blue':      '#4DA6FF',
        'hub-text':      '#EAECEF',
        'hub-muted':     '#848E9C',
        'hub-disabled':  '#474D57',
      }
    }
  }
}
```

---

# Content Structure & Hierarchy

```
home.html
├─ 状态栏 (44px)
├─ 顶部导航 (52px) [Sales Hub | 搜索 铃铛]
├─ 滚动内容区
│  ├─ 高价值客户榜单
│  │  ├─ Section Header + AB切换 [版本A] [版本B]
│  │  ├─ 版本A: 综合榜单 (5张客户卡片)
│  │  └─ 版本B: 子Tab [综合|现货|合约] + 对应榜单
│  ├─ 高潜力客户榜单
│  │  ├─ Section Header
│  │  └─ 排名卡片 (3张，含利用率进度条)
│  └─ 今日行动
│     ├─ Section Header + AB切换 [版本A] [版本B]
│     ├─ 版本A: 未开始列表 (3条)
│     └─ 版本B: [未开始(3)] + [跟进中(2)] 分组
└─ 底部Tab (56px) [首页★ | 客群 | 事件(3) | 我的]

clients.html
├─ 顶部导航 [客群 | 搜索]
├─ 筛选条 (水平滚动pills)
├─ 统计汇总行 (3格)
├─ 客户列表 (10行)
└─ 底部Tab [首页 | 客群★ | 事件 | 我的]

client-detail.html
├─ 顶部导航 [← 王伟明 | ⋮]
├─ 客户头部卡片 (头像 + 系统Tag + BD标签)
├─ 核心指标 2×3 网格
├─ 业务线明细 (可折叠)
├─ BD备注 (可编辑)
├─ 最近事件 (3条)
├─ 跟进记录时间线 (3条)
└─ 底部固定: [+ 添加跟进记录]

event-thread.html
├─ 顶部导航 [← 大额出金预警 | 🔴]
├─ 事件数据卡片
├─ 任务状态条 (四态（未开始/跟进中/已结束/忽略）切换，JS交互)
├─ AI行动建议卡片
├─ AI话术模板 (可编辑/复制)
├─ 跟进记录时间线 + 输入框
└─ 无底部Tab (二级页面)

events.html
├─ 顶部导航 [事件中心 | 筛选 3]
├─ 状态Tab [全部|未开始|跟进中|已结束|忽略]
├─ 事件类型Pills (水平滚动)
├─ 事件列表 (12条，分页或全量)
└─ 底部Tab [首页 | 客群 | 事件★(3) | 我的]
```

---

# Special Requirements

**Crypto-Finance Dark Style Guidelines:**
- NO white backgrounds anywhere. Even "light" elements use `#1E2329` or `#2B3139`
- Gold (#F0B90B) is the ONLY accent color — use sparingly for emphasis, never as background fill on large areas
- All monetary values: right-aligned in tables, use monospace-style spacing
- Loss values always red `#F6465D`, gain values always green `#0ECB81`

**AB Test Version Toggle Behavior:**
- Both versions' HTML exist in the DOM simultaneously
- JS `onclick` on toggle buttons: add `hidden` class to inactive version, remove from active
- Default on load: Version A active
- Toggle state is NOT persisted (resets on reload — acceptable for prototype)
- Visual distinction: active toggle has gold background, inactive has dim gray

**Event Four-State Machine (event-thread.html):**
```
未开始 → [点击"开始跟进"] → 跟进中 → [点击"标记完成"] → 已结束
                                    → [点击"忽略"]    → 忽略
忽略 → [点击"重新打开"] → 未开始
```
Implement entirely in vanilla JS, update badge color/text + swap action buttons on click.

**AI Talk Script Editing:**
- Default state: textarea is `readonly`, edit button shows pencil icon
- Click "编辑": remove `readonly`, textarea gets focus, button changes to "保存"
- Click "保存": re-add `readonly`, show success toast "已保存" for 2 seconds

**Navigation Between Pages:**
- All client name links → `client-detail.html`
- All event row taps → `event-thread.html`
- Bottom tab "客群" → `clients.html`
- Bottom tab "事件" → `events.html`
- Bottom tab "首页" → `home.html`
- Use `<a href="...">` for navigation

**Typography Precision:**
- Page/section titles: `16px font-semibold #EAECEF`
- Section subtitles: `12px #848E9C`
- Card metric values (large): `20-24px font-bold`
- Card labels: `11px #848E9C uppercase tracking-wide`
- Body text: `14px #EAECEF`
- Meta/time text: `11px #474D57`

**Accessibility Minimums:**
- All tap targets ≥ 44px × 44px
- Text contrast ratio ≥ 4.5:1 for body text on `#1E2329`
- State changes communicated via both color AND text (not color alone)

---

# Output Format

Please output **6 complete independent HTML files**:

1. `index.html` — 原型入口，iframe + 页面选择器
2. `home.html` — 首页（含AB版本切换JS逻辑）
3. `clients.html` — 客户列表
4. `client-detail.html` — 客户详情（王伟明为默认展示数据）
5. `event-thread.html` — 事件线程（大额出金预警为默认，含四态（未开始/跟进中/已结束/忽略）JS）
6. `events.html` — 事件中心

Each file must:
1. Be completely self-contained (no external local dependencies)
2. Include Tailwind CSS CDN + FontAwesome CDN in `<head>`
3. Include Tailwind custom config `<script>` block before Tailwind CDN
4. Simulate iPhone 15 Pro chrome: `max-w-[393px] mx-auto` with status bar and safe area
5. Display correctly at 393px width on both mobile and desktop browsers
6. Have all Chinese text (no English UI labels except crypto terminology like USDT, BTC, etc.)
7. Have fully working interactive elements (AB toggles, state machine, edit mode)
8. Use real mock data as specified — no "Lorem Ipsum", no "[placeholder]"
9. Body font: `font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif`
10. Dark background even on desktop outside the phone frame: `body { background: #000 }`

Output each file as a separate code block labeled with the filename.
