# Sales Hub

以资金沉淀为北极星的销售工作台。当前仓库处于概念验证阶段，内容由产品文档、模拟数据脚本和静态高保真原型组成；它还不是正式的前端应用工程。

## 当前事实源

### 产品与业务

- 产品定位与核心数据口径：`docs/product-concept-v2.md`
- 净利润贡献与业务口径：`docs/业务逻辑梳理.md`

### 原型实现

- 原型入口：`prototype/index.html`
- 当前首页版本：`prototype/home-a.html`、`prototype/home-b.html`、`prototype/home-c.html`
- 其他原型页面：`prototype/clients.html`、`prototype/client-detail.html`、`prototype/events.html`、`prototype/event-thread.html`、`prototype/profile.html`

说明：

- `prototype/` 目录下的 HTML 页面是当前原型形态的最终事实源。
- `docs/prototype-prompt-v2.md` 是生成这些页面时使用的上游 prompt 资产，适合作为设计意图参考，但不应替代 `prototype/` 目录本身作为页面清单事实源。

### 模拟数据链路

```text
scripts/simulate_clients.py
  -> data/clients_simulation.csv
  -> scripts/generate_prototype.py
  -> prototype/mock-data.js
  -> prototype/home-a.html
  -> prototype/home-b.html
  -> prototype/home-c.html
  -> prototype/clients.html
```

说明：

- `prototype/mock-data.js` 是当前原型运行时共享数据的直接事实源。
- 首页三版本、客群页、详情页、事件页、事件线程页和个人页现在都消费同一份 mock data contract。
- `profile.html` 的设置项仍是静态原型，但 BD 身份、统计和重点客户已经改为从共享数据派生。

## 当前文件状态

### 正在使用

- `docs/product-concept-v2.md`
- `docs/业务逻辑梳理.md`
- `docs/prototype-prompt-v2.md`
- `prototype/index.html`
- `prototype/home-a.html`
- `prototype/home-b.html`
- `prototype/home-c.html`
- `prototype/clients.html`
- `prototype/client-detail.html`
- `prototype/events.html`
- `prototype/event-thread.html`
- `prototype/profile.html`
- `scripts/simulate_clients.py`
- `scripts/generate_prototype.py`
- `data/clients_simulation.csv`

### 历史遗留，保留作参考

- `docs/prototype-prompt.md`
- `prototype/home.html`
- `docs/archive/product-concept-v1.md`（旧版产品概念）
- `docs/archive/主动观察核心字段计算公式及确认清单.md`
- `docs/archive/主动观察榜单定义.md`

以上文件对应旧版叙事，不再作为当前事实源。

## 已知缺口

1. 页面数据源已经统一到共享 mock data；剩余缺口主要在设置项、鉴权和真实用户上下文仍是静态原型。
2. 业务口径尚未最终冻结：综合净贡献、理财净贡献、U 卡净贡献、云矿机净贡献等仍有待业务/数据确认。
3. 模拟数据仍偏演示用途：`data/clients_simulation.csv` 里的 `value_source` 当前全部为 `双仓合约`，不够真实。
4. prompt 资产与原型实现曾发生版本切换：阅读仓库时优先信任本 README 和 `prototype/` 当前页面。

## 常用命令

生成模拟客户数据：

```bash
python3 scripts/simulate_clients.py
```

用模拟数据刷新首页和客群页：

```bash
python3 scripts/generate_prototype.py
```

在本机打开原型入口：

```bash
open prototype/index.html
```

## 接手建议顺序

1. 先决定未来真实用户上下文怎么进入页面，避免当前“由共享 mock data 派生 BD 身份”的方式和正式鉴权模型脱节。
2. 再继续收紧业务字段口径，避免 mock data 与产品定义继续漂移。
3. 等原型与口径稳定后，再决定是否迁移为正式前端工程。
