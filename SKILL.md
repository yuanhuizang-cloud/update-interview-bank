---
name: update-interview-bank
description: Use this skill when the user wants to maintain, expand, or tidy their personal interview question bank — the collection of interview questions and answers (面试题 / 八股 / 面试问答) they keep in a repo and study through an offline practice page (题库 / backend-interview / 刷题页). This covers extracting new questions from ChatGPT, 豆包, or Gemini conversations (or from what the user pastes), classifying and scrubbing them, writing them into the bank, and rebuilding the practice page. Trigger whenever the user asks to 整理 / 汇总 / 提取 / 补充 / 更新 / 加进 interview questions into a 题库、面试仓库 or 刷题页 — even with casual wording like 「那个面试仓库」「刷题的 html」, with or without naming the repo or skill. Do not use it to answer a single interview or algorithm question, summarize an unrelated conversation, or run routine git/GitHub tasks.
---

# 更新后端面试题库

从用户过往在 ChatGPT / 豆包 / Gemini 里的会话中，提取**面试相关**的问答，整理成结构化题库并推送到公开 GitHub 仓库。

## 仓库与关键文件

仓库根目录 = **本 skill 所在目录**（`SKILL.md` 所在的那一层）。工具脚本、题库正文、刷题页都在这个目录下，按相对路径访问即可。

```
SKILL.md                  # 本文件
content/                  # ★ 题库正文（git 跟踪），按「一级/二级」目录组织
data/questions.json       # 构建产物（由 content 编译，gitignore）
data/raw/                 # ★ 原始全量会话（gitignore，含隐私，绝不提交）
index.html                # 离线刷题器（构建产物，gitignore，双击即开）
tools/build.mjs           # content/**/*.md → questions.json → index.html
tools/template.html       # 刷题页模板（内嵌 __QUESTIONS_JSON__ 占位符）
tools/extract/            # 抓取脚本（见下）
tools/classify/gen_*.py   # 分类生成器（把抓取结果映射成 content 文件）
tools/classify/scrub_pii.example.py  # 脱敏脚本模板（复制后填自己的映射）
tools/classify/scrub_pii.py          # ★ 真实脱敏脚本（gitignore，含本人 PII 映射，仅本地）
```

## 首次准备（一次性）

1. `npm install`（安装 playwright）。
2. 复制脱敏模板并填入你自己的映射：`cp tools/classify/scrub_pii.example.py tools/classify/scrub_pii.py`，编辑其中的 `REPLACEMENTS`（真实姓名 → 通用词、公司/项目名 → 通用词等）。该文件被 gitignore，绝不提交。

## 题目数据模型（每题一个 md）

```markdown
---
id: go-slice-intersection      # 全局唯一，英文短横线
type: 手撕代码                  # 概念题 / 手撕代码 / 场景题 / 项目题 / 八股 / 其他
difficulty: easy               # easy / medium / hard
tags: [切片, map, 交集]         # 数组
sources: [gemini]              # chatgpt / doubao / gemini
date: 2026-11-12
---

## 题目
...
## 回答
...
```

- 分类由**目录路径**决定（`content/<一级>/<二级>/题.md`），frontmatter 里不重复写分类。
- 同题在多个平台问过 → 合并为一题，`sources` 写多个。

## 两级分类体系（后端导向）

| 一级 | 二级 |
|------|------|
| AI 与大模型 | 大模型原理 / 工程化 / 网关与计费 |
| 编程语言 | Go / 通用语法与并发 |
| 微服务与分布式 | RPC与服务网格 / 消息队列 / 工作流与调度 / 分布式一致性与事务 |
| 面试与职业 | 模拟面试 / 简历与求职 |
| 容器与云原生 | Kubernetes / Docker / 沙箱与隔离 / 云平台 |
| 系统设计 | 通用设计题 / 架构设计 |
| 工程化与工具 | 性能分析 / 测试 / Linux命令行 / Git |
| 数据库 | MySQL / 其他存储 |
| 算法与数据结构 | 数组与二分查找 |

分类可在实际内容需要时增补二级类。

## 增量更新原则（重要，默认必须遵守）

**只做增量，不做全量重跑。** 原因：全量重抓会再次撞上 ChatGPT 限流、浪费大量时间，还会重复覆盖已脱敏内容重新引入 PII。

- **抓取增量**：先读 `data/raw/<platform>/all.json` 已有的会话 id（或标题），只抓**新增**的会话，不要重抓已抓过的。
- **分类增量**：检查 `content/` 下已存在的题（或 `data/questions.json` 里的 id），只写**新题**，不覆盖、不重复。同名/同主题的题合并到已有的 `sources` 里，不新建重复文件。
- **构建可以全量**：`node tools/build.mjs` 是幂等的快速重编译（content → questions.json → index.html），每次都可以跑，不涉及网络、不会限流。
- **提交增量**：只提交新增/修改的文件。

## 工作流程

### 路径 A：从平台提取新会话

**1. 登录（一次性）**：`cd <仓库> && node tools/extract/login.mjs`
- 弹出可见 Chrome（三个标签页：chatgpt.com / doubao.com / gemini.google.com），用户扫码/密码登录。
- 脚本自动探测登录态，全登录后自动关闭，登录态存 `.browser-profile/`（gitignore）。

**2. 抓取**：按平台分别跑，输出到 `data/raw/<platform>/all.json`：
- 豆包：`node tools/extract/doubao.mjs`（走内部接口 batch_get + chain/single，最快最干净）
- Gemini：`node tools/extract/gemini.mjs`（DOM：`conversations-list gem-nav-list-item` + `query-text`/`markdown`）
- ChatGPT：`node tools/extract/chatgpt.mjs`（必须 headed；列表用响应拦截，详情用 DOM `group/user-message` + `group/app-widget`）
- ChatGPT 备选：用户在 app 里「设置→数据控制→导出」下载 zip → `node tools/extract/parse-export.mjs <zip路径>`

**3. 分类**：编辑 `tools/classify/gen_<platform>.py`，往 `M` 列表加 `(会话标题, 用户问题序号, id, 一级, 二级, 题型, 难度, [tags])`，然后 `python3 tools/classify/gen_<platform>.py`。先读 `data/raw/<platform>/all.json` 确认真实题型分布，再定分类。

**4. 脱敏**：`python3 tools/classify/scrub_pii.py`（每次 gen 之后都要跑，因为 gen 会从原始数据重新覆盖 content、重新引入 PII）。

**5. 构建**：`node tools/build.mjs`

**6. 提交推送**：`git add -A && git commit && git push`。

### 路径 B：用户直接提供问答

用户粘贴/给文件时，直接按上面数据模型写 `content/<一级>/<二级>/<slug>.md`，然后脱敏 → 构建 → 推送。可跳过抓取。

## 关键注意事项（都是踩过的坑）

- **ChatGPT 必须 `headless: false`**：chatgpt.com 会拦截无头浏览器，返回空白页。
- **Google OAuth 需要 stealth**：启动 Playwright 时带 `ignoreDefaultArgs:['--enable-automation']` 和 `args:['--disable-blink-features=AutomationControlled']`，否则 `navigator.webdriver=true`，Google 登录报「此浏览器或应用可能不安全」。
- **ChatGPT 抓太快会限流**：快速导航几十个会话后，后续会话会显示「无法加载此 ChatGPT 对话」。用 `retry-chatgpt.mjs` 补抓（更长等待 + 重试），或控制抓取节奏。
- **隐私是第一优先级**：`data/raw/`（原始全量会话）和 `tools/classify/scrub_pii.py`（含真实姓名/公司 PII 映射）都 gitignore，**绝不能提交或公开**。脱敏要覆盖姓名、简历文件名、公司名、项目名、内网域名/IP、住址等。
- 公开仓库意味着内容可被任何人看到，脱敏后再推送。
