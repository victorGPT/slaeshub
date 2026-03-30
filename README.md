# Sales Hub

以资金沉淀为北极星的销售工作台 MVP 原型。当前仓库处于概念验证阶段，内容由产品文档、模拟数据脚本和静态高保真原型组成；它还不是正式的前端应用工程。

## 原型页面

| 文件 | 说明 |
| --- | --- |
| `prototype/home.html` | 首页（资沉总量/流失/增长三Tab） |
| `prototype/clients.html` | 全部客户列表（搜索+状态筛选） |
| `prototype/client-detail.html` | 客户详情（资沉为核心） |
| `prototype/events.html` | 事件中心（占位） |
| `prototype/event-thread.html` | 事件线程（占位） |
| `prototype/profile.html` | 个人页面 |

## 当前事实源

### 产品与业务

- 产品定位与核心数据口径：`docs/product-concept-v2.md`
- 净利润贡献与业务口径：`docs/业务逻辑梳理.md`

### 模拟数据链路

```text
scripts/simulate_clients.py
  -> data/clients_simulation_v2.csv
  -> scripts/generate_prototype.py
  -> prototype/mock-data.js
  -> prototype/home.html, clients.html, client-detail.html, profile.html
```

说明：

- `prototype/mock-data.js` 是当前原型运行时共享数据的直接事实源。
- 首页、客群页、详情页和个人页消费同一份 mock data contract。
- `events.html` 和 `event-thread.html` 当前为静态占位页，不依赖 mock-data.js。
- `profile.html` 的设置项仍是静态原型，但 BD 身份、统计和重点客户已经改为从共享数据派生。

## 常用命令

生成模拟客户数据并刷新原型：

```bash
python3 scripts/simulate_clients.py
python3 scripts/generate_prototype.py
open prototype/home.html
```

## 归档说明

旧版"高价值/高潜力"叙事的产品文档已归档至 `docs/archive/`，包括：

- `docs/archive/product-concept-v1.md`（旧版产品概念）
- `docs/archive/主动观察核心字段计算公式及确认清单.md`
- `docs/archive/主动观察榜单定义.md`

旧版原型入口 `prototype/home-a.html`、`prototype/home-b.html`、`prototype/home-c.html` 为历史遗留，已被 `prototype/home.html` 取代。`docs/prototype-prompt.md` 为 v1 prompt 资产，当前版本为 `docs/prototype-prompt-v2.md`。

## 已知缺口

1. 事件系统需要对齐资沉框架，当前为占位状态。
2. 业务口径尚未最终冻结：综合净贡献、理财净贡献、U 卡净贡献、云矿机净贡献等仍有待业务/数据确认。
3. 模拟数据仍偏演示用途。
4. 设置项、鉴权和真实用户上下文仍是静态原型。

## 接手建议顺序

1. 先决定未来真实用户上下文怎么进入页面，避免当前"由共享 mock data 派生 BD 身份"的方式和正式鉴权模型脱节。
2. 再继续收紧业务字段口径，避免 mock data 与产品定义继续漂移。
3. 等原型与口径稳定后，再决定是否迁移为正式前端工程。
