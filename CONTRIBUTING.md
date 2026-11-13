# 贡献指南

欢迎贡献题目、修 bug、改进抓取 / 分类 / 构建脚本或本 skill 本身。

## 贡献题目

题库按「一级分类 / 二级分类」的目录结构组织，每题一个 Markdown 文件。

```
content/
├── 编程语言/
│   ├── Go/xxx.md          # 一级=编程语言，二级=Go
│   └── 通用语法与并发/xxx.md
├── 算法与数据结构/xxx.md   # 无二级分类时直接放一级目录下
├── 数据库/MySQL/xxx.md
├── 微服务与分布式/
├── 容器与云原生/
├── AI与大模型/
├── 系统设计/
└── 面试与职业/
```

新增一道题：在对应目录新建 `.md`，模板如下：

```markdown
---
id: go-slice-traversal          # 全局唯一，英文短横线
type: 概念题                     # 概念题 / 手撕代码 / 场景题 / 项目题 / 八股 / 其他
difficulty: medium              # easy / medium / hard
tags: [Go, 切片, 性能]           # 数组
sources: [gemini]               # chatgpt / doubao / gemini
date: 2026-11-13
---

## 题目
Go 切片按行遍历和按列遍历，性能差异是什么？为什么？

## 回答
这里写答案，支持 `行内代码`、``` 代码块 ```、**加粗**。
```

## 重新构建

```bash
npm run build
```

会把 `content/**/*.md` 编译成 `data/questions.json`，并内嵌进根目录的 `index.html`。

## 规范

- `id` 全局唯一、英文短横线（如 `go-slice-traversal`）。
- 一道题只放一个「## 题目」和「## 回答」。
- 分类由**目录路径**决定，frontmatter 里不必重复写分类。
- 若同一题在多个平台问过，把多个来源写进 `sources`，合并为一题，不要重复建文件。
- **内容不得含个人 / 身份信息**：姓名、简历文件名、公司名、项目名、内网域名 / IP、住址等一律脱敏。

## 贡献脚本 / skill

- 抓取脚本在 `tools/extract/`（Node + Playwright），分类生成器在 `tools/classify/`（Python）。
- 分类生成器以 `gen_gemini.py` / `gen_chatgpt.py` 为模板，新增平台可照此实现。
- 修改 skill 行为时，同步更新 `SKILL.md` 与 `README.md`。
- 提交前请确认未包含 `data/raw/`、`.browser-profile/`、`tools/classify/scrub_pii.py` 等被 gitignore 的隐私文件。
