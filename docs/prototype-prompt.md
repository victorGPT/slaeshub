# Sales Hub — 原型生成 Prompt

> 将此 prompt 完整提供给 AI 工具（如 Claude / Cursor）来生成原型代码。
>
> Legacy note: this file describes the v1 prototype flow centered on `home.html`. In the current repository, `prototype/home.html` is retained only as historical reference. The active homepage entry flow is `prototype/index.html` -> `home-a.html` / `home-b.html` / `home-c.html`.

---

# Role

You are a world-class UI/UX engineer and frontend developer specializing in fintech and crypto exchange mobile interfaces. You excel at creating dark-themed, data-rich dashboards with clean information hierarchy using Tailwind CSS. You have deep experience building mobile-first PWA applications for financial professionals.

# Task

Create a high-fidelity multi-page mobile prototype (HTML + Tailwind CSS) for **Sales Hub** — a BD (Business Development) workspace for a crypto exchange serving VIP institutional clients.

Design style: **Dark crypto fintech** — professional, data-dense but readable, dark backgrounds with accent colors for key metrics and actions. Core keywords: 专业金融感、暗色主题、数据密度高、操作路径清晰、移动端优先.

The prototype must demonstrate the complete BD workflow:
1. BD opens app → sees client list with key metrics
2. Taps a client → views 360° data dashboard
3. Sees event feed for that client → taps an event card
4. Views event thread with AI-generated action suggestion and talk script
5. Chooses to follow up or ignore → records feedback

# Tech Stack

- **File Structure**: Multi-page HTML files with shared navigation
  - `index.html` — entry point with iframe to host pages, simulating iPhone 15 Pro device frame
  - `home.html` — homepage: rankings + today's actions (with A/B version toggles)
  - `clients.html` — client list
  - `client-detail.html` — client 360° dashboard
  - `events.html` — event feed (all clients)
  - `event-thread.html` — single event thread detail
  - `profile.html` — BD profile / settings
- **Framework**: Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`)
- **Icons**: FontAwesome 6 via CDN (`<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">`)
- **Device Simulation**: iPhone 15 Pro (393px × 852px), with rounded corners (border-radius: 44px), iOS status bar simulation
- **Images**: Use `https://ui-avatars.com/api/?name=XXX&background=random&color=fff&size=96` for client avatars
- **Font**: System sans-serif (`-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`)
- **Language**: All UI text in Simplified Chinese (简体中文)

# Visual Design Requirements

## 1. Color Palette

**Background Colors:**
- App Background: #0B0E11 (deep dark, similar to Binance dark mode)
- Card Background: #1E2329 (elevated surface)
- Card Background Hover: #2B3139 (interactive state)
- Input/Field Background: #2B3139
- Modal Overlay: rgba(0, 0, 0, 0.7)

**Primary Colors:**
- Brand Gold: #F0B90B (primary accent — key metrics, active tabs, primary buttons)
- Brand Gold Hover: #D4A50A (button hover state)

**Status Colors:**
- Profit Green: #0ECB81 (positive values, success, gains)
- Loss Red: #F6465D (negative values, errors, losses, urgent events)
- Warning Orange: #F0B90B (warnings, pending items)
- Info Blue: #1E88E5 (informational, links)
- Neutral Blue: #5E6673 (secondary actions)

**Text Colors:**
- Primary Text: #EAECEF (titles, key content)
- Secondary Text: #848E9C (descriptions, labels)
- Tertiary Text: #5E6673 (hints, disabled)
- Inverse Text: #0B0E11 (text on gold buttons)

**UI Element Colors:**
- Divider: #2B3139 (subtle separators)
- Border: #2B3139 (card borders when needed)
- Badge Background: #F6465D (notification badges)

## 2. UI Style Characteristics

**Cards:**
- Background: #1E2329
- Border Radius: 12px (rounded-xl)
- Border: none (rely on background contrast)
- Padding: 16px
- Spacing between cards: 12px

**Buttons:**
- Primary: Gold background (#F0B90B), dark text (#0B0E11), height 44px, radius 8px
- Secondary: Transparent background, 1px border #2B3139, text #EAECEF, height 44px, radius 8px
- Danger: Red background (#F6465D), white text, height 44px, radius 8px
- Ghost: No background, gold text (#F0B90B), no border
- Active State: opacity 85%

**Metric Cards (数字卡片):**
- Large number: 24px bold, color varies by meaning (gold for neutral, green for positive, red for negative)
- Label below: 12px, #848E9C
- Layout: horizontal scroll or 2-column grid

**Tags/Badges:**
- Background: semi-transparent color (e.g., rgba(14, 203, 129, 0.15) for green tags)
- Text: corresponding solid color
- Padding: 4px 8px
- Border Radius: 4px
- Font Size: 12px

**List Items:**
- Height: 72px
- Layout: Avatar (40px circle) + Name (15px bold #EAECEF) + Subtitle (13px #848E9C) + Right metric/arrow
- Divider: 1px #2B3139, full width
- Active State: background #2B3139

**Event Cards (事件卡片):**
- Left border: 3px solid, color indicates type (red=urgent, gold=action, green=positive, blue=info)
- Background: #1E2329
- Padding: 16px
- Contains: event type tag + title + summary + timestamp + status badge
- Border Radius: 12px

## 3. Layout Structure (Mobile View - 393px)

**Status Bar (44px):**
- Simulated iOS status bar with time, signal, battery
- Background: #0B0E11

**Top Navigation Bar (56px):**
- Title: Left-aligned, 18px bold, #EAECEF
- Right side: notification bell icon with red badge
- Background: #0B0E11
- Bottom border: 1px #2B3139

**Content Area:**
- Padding: 16px left/right
- Scroll: vertical, smooth
- Bottom padding: 80px (space for tab bar)

**Bottom Tab Bar (56px + 34px safe area = 90px total):**
- 4 tabs: 客户 / 事件 / 数据 / 我的
- Icons: FontAwesome, 20px
- Label: 10px
- Active: Gold (#F0B90B) icon + text
- Inactive: Gray (#5E6673) icon + text
- Background: #1E2329
- Top border: 1px #2B3139
- Position: fixed bottom

## 4. Page Content Specifications

### Page 1: 首页 (home.html) — Home Tab

**Top Bar:**
- Title: "Sales Hub"
- Right: bell icon (fa-bell) with red dot badge

**=== 上半屏：客户排行榜 ===**

需要出两个布局版本（Version A 和 Version B），在同一个 HTML 文件内用 tab 切换展示。

**Version A — 折叠模式:**
- 默认展开"今日交易量 Top 5"排行榜
- "沉淀资金 Top 5"和"本周盈亏 Top 5"折叠为可点击展开的标题行
- 每个排行项: 排名序号 + 客户头像 + 名称 + 数值（右对齐，font-mono）
- 折叠标题行右侧显示 chevron-down 图标

**Version B — 紧凑模式:**
- 三个排行榜纵向排列，每个只展示 Top 3
- 每个排行区块: 标题行 + 3 条排行项 + "查看全部 →" 链接
- 排行项更紧凑: 排名 + 头像(32px) + 名称 + 数值

**顶部添加版本切换按钮:** 两个小按钮 "版本A" / "版本B"，用 JavaScript 切换显示，方便体验对比。

**排行 Mock 数据:**

今日交易量 Top 5:
| # | 客户 | 交易量 |
|---|------|--------|
| 1 | 陈志强 (Alpha Trading) | $4,230,000 |
| 2 | 张伟 (Whale Capital) | $3,870,000 |
| 3 | 周雅琴 (Genesis Holdings) | $2,910,000 |
| 4 | 刘洋 (Momentum Capital) | $1,650,000 |
| 5 | 赵雪梅 (个人大户) | $1,120,000 |

沉淀资金 Top 5:
| # | 客户 | 沉淀资金 |
|---|------|----------|
| 1 | 周雅琴 (Genesis Holdings) | $8,420,000 |
| 2 | 陈志强 (Alpha Trading) | $6,150,000 |
| 3 | 张伟 (Whale Capital) | $4,890,000 |
| 4 | 李明远 (Dragon Fund) | $3,210,000 |
| 5 | 黄海涛 (个人大户) | $2,740,000 |

本周盈亏 Top 5:
| # | 客户 | 本周盈亏 |
|---|------|----------|
| 1 | 周雅琴 (Genesis Holdings) | +$528,000 |
| 2 | 陈志强 (Alpha Trading) | +$312,000 |
| 3 | 张伟 (Whale Capital) | +$182,400 |
| 4 | 刘洋 (Momentum Capital) | +$156,000 |
| 5 | 王芳 (个人大户) | -$23,000 |

- 盈利绿色，亏损红色
- 点击排行项 → 跳转 client-detail.html

**=== 下半屏：今日行动 ===**

需要出两个内容版本（Version A 和 Version B），同样用 tab 切换。

**Version A — 仅待处理:**
- Section title: "待处理事件" + 红色数字 badge "5"
- 展示 5 条待处理事件卡片（简化版：左色条 + 类型标签 + 标题 + 时间）
- 底部: "查看全部事件 →" 链接跳转 events.html

**Version B — 待处理 + 跟进中:**
- Section 1: "待处理" + badge "5"，展示 3 条
- Section 2: "跟进中" + badge "3"，展示 3 条
- 两个 section 视觉上用分隔线区分
- 底部: "查看全部事件 →"

**顶部同样添加 "版本A" / "版本B" 切换按钮（独立于排行榜版本切换）。**

事件 Mock 数据复用 Page 3 事件中心的数据。

### Page 2: 客户列表 (clients.html) — 客户 Tab

**Top Bar:**
- Title: "我的客户"
- Right: search icon (fa-search)

**Search Bar (点击 search icon 后展开):**
- Background: #2B3139
- Placeholder: "搜索客户名称..."
- Height: 40px, radius 8px

**Client List:**
Mock 8 clients with realistic Chinese names and data:

| 客户名 | 标签 | 右侧指标 |
|--------|------|----------|
| 张伟 (Whale Capital) | 🐋 鲸鱼 · 高频 | 本月盈利 +$182K |
| 李明远 (Dragon Fund) | 📊 机构 · 稳健 | 本月盈利 +$94K |
| 王芳 (个人大户) | 💎 高净值 · 短线 | 本月盈利 -$23K |
| 陈志强 (Alpha Trading) | 🏛 机构 · 套利 | 本月盈利 +$312K |
| 赵雪梅 (个人大户) | ⚡ 高频 · 合约 | 本月盈利 +$67K |
| 刘洋 (Momentum Capital) | 📊 机构 · 趋势 | 本月盈利 +$156K |
| 黄海涛 (个人大户) | 💎 高净值 · 现货 | 本月盈利 +$41K |
| 周雅琴 (Genesis Holdings) | 🐋 鲸鱼 · 长线 | 本月盈利 +$528K |

- Profit green for positive, loss red for negative
- Each row: avatar (initials) + name + org + tags + right metric
- Tap → navigate to client-detail.html

### Page 2: 客户详情 / 360° 面板 (client-detail.html)

**Top Bar:**
- Back arrow (fa-chevron-left)
- Title: "张伟" (client name)
- Right: more options (fa-ellipsis-vertical)

**Client Header Card:**
- Avatar: 64px, circle, with initials
- Name: 张伟, 18px bold
- Organization: Whale Capital
- Tags: 🐋 鲸鱼 · 高频交易 · VIP-1
- BD备注: "偏好短线合约，脾气急，响应要快"
- "编辑备注" ghost button

**Metric Cards Grid (2 columns):**
| 指标 | 值 | 颜色 |
|------|-----|------|
| 本月盈利 | +$182,400 | green |
| 累计交易额 | $12.4M | gold |
| 已投入福利 | $8,200 | blue |
| 可投入福利 | $36,480 | gold |
| 现货持仓 | $2.1M | #EAECEF |
| 合约持仓 | $4.8M | #EAECEF |

**业务分布 (简化柱状图):**
- 用 CSS 柱状图模拟：现货 30%, 合约 55%, 理财 10%, U卡 5%
- 每个柱子用不同颜色，下方标注业务名和百分比

**最近事件 (Latest Events - 显示最近3条):**
- 事件卡片列表（简化版），点击可跳转 event-thread.html
- 底部: "查看全部事件 →" 链接

**跟进记录 (Recent Follow-ups - 显示最近3条):**
- 时间线样式，每条记录: 时间 + BD名字 + 简短描述
- 例: "03-26 14:30 — 张三：客户反馈合约延迟问题已解决，表示满意"
- 底部: "添加记录" primary button

### Page 3: 事件中心 (events.html)

**Top Bar:**
- Title: "事件中心"
- Right: filter icon (fa-filter)

**Filter Tabs (horizontal scroll):**
- 全部 (active, gold underline) / 待处理 / 跟进中 / 已完成 / 已忽略
- Active tab: gold text + 2px bottom border
- Inactive: gray text

**Event Cards List:**

Mock 6 events:

**Event 1 (urgent, red left border):**
- Type tag: "⚠️ 大额爆仓" (red tag)
- Title: "张伟 — 合约爆仓 $320,000"
- Summary: "BTC/USDT 永续合约多单，预计损失 $320K。客户情绪可能波动较大。"
- Time: "10 分钟前"
- Status: 🔴 待处理

**Event 2 (action, gold left border):**
- Type tag: "🎁 盈利奖励" (gold tag)
- Title: "周雅琴 — 本月盈利达标 $528K"
- Summary: "建议投入福利 $105,600（盈利的 20%），可考虑高端礼品或 VIP 活动邀请。"
- Time: "2 小时前"
- Status: 🔴 待处理

**Event 3 (info, blue left border):**
- Type tag: "💰 大额充值" (blue tag)
- Title: "陈志强 — USDT 充值 $500,000"
- Summary: "非常规时间充值，可能在布局新仓位。建议了解交易意向。"
- Time: "3 小时前"
- Status: 🟡 跟进中

**Event 4 (urgent, red left border):**
- Type tag: "🔧 系统反馈" (red tag)
- Title: "李明远 — 反馈合约下单延迟"
- Summary: "客户通过 Telegram 反馈合约下单有 2-3 秒延迟，影响其高频策略。"
- Time: "5 小时前"
- Status: 🟡 跟进中

**Event 5 (action, gold left border):**
- Type tag: "📊 异常行为" (gold tag)
- Title: "王芳 — 连续 3 天大额提现"
- Summary: "累计提现 $180K，可能存在流失风险。建议主动沟通了解原因。"
- Time: "昨天 18:30"
- Status: 🔴 待处理

**Event 6 (positive, green left border):**
- Type tag: "✅ 跟进完成" (green tag)
- Title: "赵雪梅 — U 卡消费异常已确认"
- Summary: "已确认为客户本人操作，连续两笔相同金额为正常购物行为。"
- Time: "昨天 11:20"
- Status: 🟢 已完成

### Page 4: 事件线程详情 (event-thread.html)

**Top Bar:**
- Back arrow
- Title: "事件详情"
- Right: more options

**Event Header:**
- Type tag: "⚠️ 大额爆仓" (red tag, large)
- Title: "张伟 — 合约爆仓 $320,000", 18px bold
- Time: "2026-03-27 14:23"
- Status badge: "待处理" (red background)

**关联数据卡片 (Associated Data):**
- 爆仓合约: BTC/USDT 永续 · 多单
- 爆仓金额: $320,000 (red)
- 当前 BTC 价格: $67,420
- 客户当前总持仓: $4.8M
- 客户本月盈利: +$182,400 → 变为 -$137,600 (red, with arrow showing change)

**AI 行动建议卡片 (Action Suggestion):**
- Card with special styling: border 1px dashed #F0B90B, background #1E2329
- Header: "🤖 AI 行动建议" with sparkle icon
- Suggestion text:
  ```
  建议立即联系客户张伟。该客户偏好短线合约，性格较急，
  爆仓后情绪波动可能较大。

  建议行动：
  1. 15 分钟内通过 Telegram 主动联系
  2. 表达关心，避免直接提及具体亏损数字
  3. 可提供 VIP 手续费折扣作为安抚措施
  4. 如客户情绪激动，建议安排视频通话
  ```

**AI 话术模板 (Talk Script):**
- Card background: #2B3139
- Header: "💬 参考话术" with copy button (fa-copy)
- Script text:
  ```
  张总您好，我是您的专属客户经理。注意到市场刚才波动
  比较大，想跟您确认一下目前的情况，看看有没有什么我
  们可以协助的地方。

  我们非常重视您作为 VIP 客户的体验，针对近期的市场
  行情，我们可以为您提供专属的手续费优惠方案，帮助您
  在后续交易中降低成本。

  您看方便的话，我们可以简单聊几分钟？
  ```
- Bottom: "📋 复制话术" button (secondary style) + "✏️ 编辑" button (ghost style)

**操作按钮区:**
- "开始跟进" primary button (gold, full width)
- "忽略此事件" ghost button (gray text, below)

**跟进记录区 (Follow-up Thread):**
- Section title: "跟进记录"
- Empty state: "暂无跟进记录" with subtle icon
- When tracking: timeline style entries
  - Each entry: avatar + BD name + time + content
  - "添加跟进记录" button at bottom

**Quick Record Input (Fixed bottom, shown after "开始跟进"):**
- Input bar fixed at bottom (above tab bar)
- Text input: placeholder "记录跟进内容..."
- Right: send button (gold, fa-paper-plane)
- Background: #1E2329

### Page 5: 我的 (profile.html)

**简化页面:**
- BD avatar + name + role
- 统计: 管理客户数 47 / 本月处理事件 34 / 完成率 85%
- Menu list:
  - 通知设置
  - 语言设置
  - 关于 Sales Hub
  - 退出登录

# Implementation Details

- Page width: max-w-[393px], centered with mx-auto, background #0B0E11
- Device frame in index.html: rounded-[44px] with overflow-hidden, border 2px #2B3139
- Layout: Flexbox primary, Grid for metric cards
- Top nav: sticky top-0 z-50
- Bottom tab bar: fixed bottom-0 w-full z-50
- Card spacing: gap-3 (12px)
- Page margins: px-4 (16px)
- All clickable elements: active:opacity-85 transition
- Smooth scrolling: scroll-smooth on body
- Numbers and amounts: use monospace font (font-mono) for alignment
- Profit/loss: green (#0ECB81) for positive, red (#F6465D) for negative, always show +/- sign
- Status bar: simulated fixed top bar with white text on dark background

# Tailwind Configuration

```javascript
tailwind.config = {
  theme: {
    extend: {
      colors: {
        'dark-bg': '#0B0E11',
        'dark-card': '#1E2329',
        'dark-hover': '#2B3139',
        'dark-border': '#2B3139',
        'brand-gold': '#F0B90B',
        'brand-gold-hover': '#D4A50A',
        'profit-green': '#0ECB81',
        'loss-red': '#F6465D',
        'info-blue': '#1E88E5',
        'text-primary': '#EAECEF',
        'text-secondary': '#848E9C',
        'text-tertiary': '#5E6673',
      },
      fontFamily: {
        'mono': ['SF Mono', 'Monaco', 'Inconsolata', 'Fira Mono', 'Droid Sans Mono', 'Source Code Pro', 'monospace'],
      }
    }
  }
}
```

# Content Structure & Hierarchy

```
Sales Hub
├─ 客户列表 (clients.html) [Tab: 客户]
│  ├─ Top Bar ("Sales Hub" + notification bell)
│  ├─ Search Bar
│  ├─ Quick Stats Row (4 cards, horizontal scroll)
│  └─ Client List (8 clients with avatar + name + tags + metric)
│     └─ Tap → client-detail.html
│
├─ 客户详情 (client-detail.html) [Stack navigation]
│  ├─ Top Bar (back + client name + options)
│  ├─ Client Header (avatar + name + org + tags + BD note)
│  ├─ Metric Cards (2×3 grid)
│  ├─ 业务分布 (CSS bar chart)
│  ├─ 最近事件 (3 event cards)
│  │  └─ Tap → event-thread.html
│  └─ 跟进记录 (timeline, 3 entries + add button)
│
├─ 事件中心 (events.html) [Tab: 事件]
│  ├─ Top Bar ("事件中心" + filter)
│  ├─ Filter Tabs (全部/待处理/跟进中/已完成/已忽略)
│  └─ Event Cards (6 events with type tag + title + summary + time + status)
│     └─ Tap → event-thread.html
│
├─ 事件线程 (event-thread.html) [Stack navigation]
│  ├─ Top Bar (back + "事件详情")
│  ├─ Event Header (type + title + time + status)
│  ├─ 关联数据 (key-value data card)
│  ├─ AI 行动建议 (dashed gold border card)
│  ├─ AI 话术模板 (copy + edit buttons)
│  ├─ Action Buttons (开始跟进 / 忽略)
│  └─ 跟进记录 Thread (timeline + input bar)
│
└─ 我的 (profile.html) [Tab: 我的]
   ├─ BD Profile (avatar + name + role)
   ├─ Stats (3 metrics)
   └─ Settings Menu List
```

# Special Requirements

- **Crypto Fintech Dark Theme:**
  - All backgrounds must be dark (#0B0E11 / #1E2329), never use light/white backgrounds
  - Gold accent (#F0B90B) used sparingly — only for primary actions, active states, and key metrics
  - Green/Red exclusively for profit/loss indicators and status
  - Maintain high contrast between text and background (WCAG AA minimum)

- **Data Display:**
  - All monetary values in USD with $ prefix
  - Use comma separators for thousands (e.g., $182,400)
  - Always prefix with +/- for profit/loss values
  - Use font-mono for all numeric values for clean alignment

- **Interaction Details:**
  - Tap feedback: opacity change to 85% on all interactive elements
  - Card press: subtle scale(0.98) transform
  - Page transitions: not required for static prototype
  - Bottom tab: active state with gold color + slight scale on icon

- **Mobile Specifics:**
  - Touch targets: minimum 44px × 44px for all tappable elements
  - Safe area: 34px bottom padding for iOS home indicator
  - Status bar: 44px fixed top, simulated with time "14:23" and battery/signal icons
  - Content must not be obscured by fixed top/bottom bars

# Output Format

Please output complete HTML files for each page, ensuring:
1. Perfect display at 393px width mobile viewport
2. Dark theme consistently applied across all pages
3. All text in Simplified Chinese
4. Realistic mock data (Chinese names, USD amounts, crypto terminology)
5. All interactive elements have visual feedback (active states)
6. Proper fixed positioning for navigation bars
7. Font-mono for all numeric/monetary values
8. Color-coded profit/loss (green/red) throughout
9. Event cards with colored left borders indicating type
10. AI suggestion card with distinctive dashed gold border styling

Start with `index.html` (device frame + iframe), then `clients.html`, `client-detail.html`, `events.html`, `event-thread.html`, and `profile.html`.
