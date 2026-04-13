# Macroscope 操作指南

> 本文档供人类用户和 AI Agent 共同参考。涵盖从初始设置到日常使用的完整流程。
> 官方文档: https://docs.macroscope.com

---

## 一、Macroscope 是什么

Macroscope 是一个 AI 驱动的代码审查与工程工作流平台，提供三大核心能力:

| 能力 | 说明 |
|------|------|
| **Agent** | AI 助手，理解代码库、git 历史和已连接工具，可回答问题并执行操作 |
| **Code Review** | 每个 PR 自动检测 bug 和策略违规，可一键修复 |
| **Status** | 代码库变更可视化：提交摘要、生产力指标、周报 |

---

## 二、初始设置（Getting Started）

### 2.1 注册并连接 GitHub

1. 前往 https://app.macroscope.com 注册
2. 授权 GitHub 组织/仓库访问
3. GitHub 连接在初始设置时自动完成，无需手动配置

### 2.2 连接 Slack（推荐，主要交互方式）

1. 进入 **Settings → Connections → Slack**
2. 由 Slack 管理员完成 OAuth 授权
3. 连接后可通过以下方式与 Macroscope 交互:
   - 直接 DM Macroscope 应用
   - 在频道中 `@Macroscope` 提及
   - 添加到群组 DM

### 2.3 配置 Status（Agent 前置要求）

> **重要**: 使用 Agent 之前必须先配置 Status。

1. 进入 Settings，填写 **Product Overview**（产品概述，帮助 AI 生成更准确的摘要）
2. 设置 **Sprint Cadence**（周报边界日期和时间）
3. 等待 **Backfill 完成**（约 1 小时，自动处理历史提交数据）
4. Backfill 完成后，Home 页面会显示近期团队活动摘要

### 2.4 可选集成

在 **Settings → Connections** 中按需连接:

| 工具 | 用途 | 设置要点 |
|------|------|----------|
| **Linear** | 查看/创建 issue | 点击 Connect Linear，选择团队权限 |
| **Jira** | 查看/创建 ticket | 建议创建专用 Jira 用户，限定项目范围 |
| **LaunchDarkly** | 查看 feature flag 状态 | 需要 Reader 角色的 API token |
| **PostHog** | 查询分析事件和趋势 | 需要个人 API key，选择 US/EU 区域 |
| **Sentry** | 搜索错误、排查崩溃 | 需要 `event:read, project:read, org:read` 权限的 token |
| **BigQuery** | 浏览数据集、运行只读 SQL | 需要 Data Viewer + Job User 角色的服务账号 |
| **GCP Cloud Logging** | 搜索应用日志 | 需要 Logs Viewer 角色的服务账号 |
| **Amplitude** | 事件分析、漏斗、留存 | 需要 API Key + Secret Key |
| **MCP Connectors** | 自定义工具扩展（仅管理员） | 粘贴 MCP 服务器 URL，配置认证 |

---

## 三、日常使用

### 3.1 Code Review（自动代码审查）

**工作方式**: 每次 PR 打开或推送时自动触发。

**仓库级配置**（Settings → Repos）:
- **Correctness**: 逻辑错误和 bug 检测（开/关）
- **Custom Rules**: 检查仓库根目录 `macroscope.md` 中定义的规则
- **Auto-summarize**: 自动生成 PR 描述
- **Auto-assign Reviewer**: PR 无 reviewer 时自动分配
- **Skip Dependabot**: 跳过 Dependabot PR
- **Skip/Always Review Labels**: 通过 label 控制是否审查

**个人配置**（Settings → Personal）:
- 可以 toggle 各项审查类型
- 可选择审查结果放在 PR description 还是 comment

**自定义审查规则**: 在仓库根目录创建 `.macroscope/` 目录，放入 markdown 文件定义规则。

### 3.2 Fix It For Me（一键修复）

当 Macroscope 在 Code Review 中发现问题时:

1. **GitHub 方式**: 回复 Macroscope 的评论，要求修复
2. **Slack 方式**: 向 `@Macroscope` 描述需要修复的问题

**自动流程**:
1. 从功能分支创建新分支（命名模式 `macroscope/*/**`）
2. 实施修复并提交
3. 打开 PR
4. 运行 CI，如果失败会尝试自动修复
5. CI 通过后自动合并（如已启用）

**控制选项**:
- `Fix it for me and auto-merge` — 强制自动合并
- `Fix it but don't auto-merge` — 留待手动审查
- 目标为 main 的 PR 始终需要手动合并

> 注意: 不支持跨仓库或 fork PR。

### 3.3 Approvability（自动批准低风险 PR）

**默认关闭**，需在 Settings → Repos → Approvability 中逐仓库启用。

**自动批准条件**（两项都必须通过）:
1. **资格评估**: 分析变更规模、代码所有权、作者角色等
   - 通常可批准: 文档、测试、feature flag 后的代码、简单 bug 修复、文案
   - 通常不可批准: 大型重构、schema 变更、安全/认证/计费代码、破坏性变更
2. **正确性验证**: Code Review 零问题

**自定义规则**: 创建 `.macroscope/approvability.md` 定义自定义资格标准。

### 3.4 Agent（AI 助手）

**交互方式**:

| 渠道 | 方法 |
|------|------|
| Slack | DM 应用、`@Macroscope` 提及、群组 DM |
| GitHub | 在 PR 中 `@macroscope-app` 提及 |
| API | POST webhook（见下文 API 节） |

**内置能力**（无需额外配置）:
- 代码搜索、git 历史分析、PR 搜索
- GitHub API 只读访问（issue、部署、release）
- 创建分支、写代码、开 PR、添加 reviewer
- 贡献者指标、Sprint 报告
- 图片生成（流程图等）、Web 搜索

**已连接服务的扩展能力**: Jira、Linear、BigQuery、PostHog、Amplitude、LaunchDarkly、Sentry、GCP Cloud Logging、MCP 自定义工具。

**自定义响应风格**: Settings → Workspace → Custom AMA Instructions。

### 3.5 Check Run Agents（自定义检查代理）[Beta]

在每个 PR 上自动运行自定义 AI 检查。

**创建方法**:
1. 在仓库根目录创建 `.macroscope/your-check.md`
2. 添加 YAML frontmatter 配置:

```yaml
title: Security Review          # GitHub UI 显示名（60字符内）
model: claude-opus-4-6          # LLM 模型选择
reasoning: low                  # 思考深度: off/low/medium/high
effort: low                     # 分析深度: low/medium/high
input: full_diff                # full_diff 或 code_object
tools: [browse_code, git_tools] # 可用工具
include: ["src/**"]             # 只审查匹配的文件
conclusion: neutral             # neutral（不阻塞）或 failure（可阻塞）
```

3. 提交到默认分支，新 PR 生效

**可用工具**: `browse_code`, `git_tools`, `github_api_read_only`, `modify_pr`, `web_tools`, `slack`, `sentry`, `bigquery`, `image_gen`, `mcp`

**编写建议**: 指令要具体（"标记超过50行无文档注释的函数" > "检查代码质量"），定义严重级别，声明什么不需要标记。

### 3.6 Macros（工作流自动化）

**三要素**: 触发器 + Agent 指令 + 投递目标

**触发类型**:
- **定时**: 每日/每周/双周
- **事件**: 新提交（可按仓库/分支过滤）、新 PR 创建（可按仓库过滤）

**投递渠道**:
- **Slack**: 发送到任意频道（私有频道需先邀请 @Macroscope）
- **Webhook**: 发送到自定义 URL（支持 Zapier、Discord、n8n 等）

**常见用例**:
- 每日按贡献者分组的活动摘要
- 每周面向非技术人员的产品更新
- 关键提交的事件告警
- PR 与 ticket 自动关联

**测试**: 用 Run Now 按钮或 Slack @Macroscope 测试后再正式启用。

### 3.7 Slack 订阅命令

```
/macroscope subscribe <repo>              # 订阅仓库全部活动
/macroscope subscribe-commits <repo>      # 提交摘要+关联 ticket
/macroscope subscribe-prs <repo>          # PR 更新
/macroscope subscribe-build-failures <repo> # 构建失败告警
```

添加 `--paths=<glob>` 过滤特定目录。

### 3.8 Areas（活动分类）

> 20人以下团队通常不需要。

将代码活动按高级别分类（如"消费者团队"、"营收团队"、"代码审查"、"平台"）。

**效果**: 自动分类提交、生成分区摘要、支持针对性查询和邮件周报。

**设置建议**: Area 描述中包含工作类型、专业术语、团队名称、关联系统。

---

## 四、API 使用

### Webhook 触发 Agent

```
POST https://hooks.macroscope.com/api/v1/workspaces/{workspaceType}/{workspaceId}/query-agent-webhook-trigger
```

**Headers**:
```
Content-Type: application/json
X-Webhook-Secret: <your-api-key>
```

**Body**:
```json
{
  "query": "上周合并了哪些 PR？",
  "responseDestination": {
    "slackChannelId": "C0123456789"
  },
  "timezone": "Asia/Shanghai"
}
```

或使用 webhook 回调:
```json
{
  "query": "...",
  "responseDestination": {
    "webhookUrl": "https://your-server.com/callback"
  }
}
```

**注意**:
- API Key 在设置 webhook 时生成，之后无法再次查看
- 外部 webhook URL 必须提前在 Settings 中加入白名单（仅 HTTPS）
- 返回 `202 Accepted`，结果异步投递到指定目标

---

## 五、计费

| 功能 | 费用 |
|------|------|
| Code Review | $0.05/KB（最低 10KB = $0.50） |
| Status（含 Agent） | $0.05/commit |
| 新工作区 | 赠送 $100 试用额度 |

**消费控制**:
- 月度消费上限（可调）
- 单次审查上限: $10（可覆盖）
- 单 PR 上限: $50（可覆盖）
- 默认开启自动充值

---

## 六、Agent 操作速查（给 AI Agent）

当需要与 Macroscope 交互时:

1. **GitHub PR 中**: 评论中 `@macroscope-app` + 指令
2. **请求修复**: 回复 Macroscope 的 review 评论说 "fix this"
3. **API 调用**: POST 到 webhook endpoint，附带 query 和 responseDestination
4. **自定义检查**: 在 `.macroscope/` 下创建 markdown 文件定义规则

**仓库配置文件**:
- `.macroscope/*.md` — Check Run Agent 定义
- `.macroscope/approvability.md` — 自动批准规则
- `macroscope.md`（仓库根目录） — 自定义代码审查规则

---

## 七、推荐的初始设置流程（Checklist）

- [ ] 注册 https://app.macroscope.com 并连接 GitHub 仓库
- [ ] 连接 Slack workspace
- [ ] 填写 Product Overview 和 Sprint Cadence（Settings）
- [ ] 等待 Backfill 完成（约1小时）
- [ ] 在 Slack 中 DM Macroscope，测试 Agent 是否正常响应
- [ ] 在仓库 Settings 中确认 Code Review 已启用
- [ ] 提交一个测试 PR，观察自动审查效果
- [ ] （可选）连接 Linear/Jira 丰富提交摘要
- [ ] （可选）创建 `.macroscope/` 目录，添加自定义检查规则
- [ ] （可选）设置 Slack 订阅命令，接收仓库动态
- [ ] （可选）启用 Approvability 自动批准低风险 PR
- [ ] （可选）创建 Macros 自动化工作流
