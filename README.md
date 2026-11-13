# update-interview-bank

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-2f6fed.svg)](#)

一个 **Claude Code Skill + 离线工具箱**：从 ChatGPT / 豆包 / Gemini 的过往会话中，提取、分类、脱敏面试问答，编译成带搜索 / 筛选 / 刷题功能的离线网页题库。

> 本仓库由个人题库维护流程提炼而来，可直接安装为 Claude Code skill，也可当作独立脚本工具使用。

## 功能

- 🤖 **Skill 化**：安装后，对 Claude Code 说「整理面试题」「把这段问答加进题库」「更新刷题的 html」即可自动触发。
- 🕷️ **自动抓取**：Playwright 抓取 ChatGPT / 豆包 / Gemini 的完整会话（支持登录态复用、限流补抓、官方导出 zip 解析）。
- 🗂️ **分类生成**：`gen_*.py` 把抓取结果按「一级 / 二级」分类映射成 `content/**/*.md`。
- 🧼 **脱敏**：`scrub_pii.py` 幂等地把姓名 / 公司 / 项目等身份信息替换为通用词（真实映射仅本地）。
- 🖥️ **离线刷题器**：`build.mjs` 把 `content/` 编译成 `index.html`（双击即开，搜索 / 筛选 / 刷题 / 进度记录，键盘 `j`/`k`/`空格` 操作）。

## 安装

```bash
# 1. 克隆到 Claude Code 的 skills 目录（目录名需与 skill 名一致）
git clone https://github.com/yuanhuizang-cloud/update-interview-bank.git \
  ~/.claude/skills/update-interview-bank

# 2. 安装依赖（playwright）
cd ~/.claude/skills/update-interview-bank
npm install

# 3. 生成脱敏脚本（填入你自己的姓名/公司映射，该文件被 gitignore）
cp tools/classify/scrub_pii.example.py tools/classify/scrub_pii.py
```

> 若只想当脚本工具用、不装 skill，clone 到任意目录即可，脚本全部按相对路径解析仓库根目录。

## 快速开始

```bash
# 1. 登录（弹出可见 Chrome，依次登录三平台，登录态保存在 .browser-profile/）
npm run login

# 2. 抓取会话 → data/raw/<platform>/all.json
node tools/extract/doubao.mjs
node tools/extract/gemini.mjs
node tools/extract/chatgpt.mjs        # ChatGPT 需可见浏览器（headless:false）

# 3. 编辑 tools/classify/gen_<platform>.py，往 M 列表加分类映射，再运行
python3 tools/classify/gen_doubao.py   # 按需自建；已提供 gen_gemini.py / gen_chatgpt.py 模板
python3 tools/classify/scrub_pii.py    # 脱敏（每次 gen 后都要跑）

# 4. 构建离线刷题器
npm run build                           # 生成 data/questions.json 与 index.html

# 5. 打开 index.html 刷题，或提交推送
```

## 目录结构

```
SKILL.md                  # Claude Code skill 定义
content/                  # 题库正文（每题一个 md，按一级/二级目录组织）
tools/build.mjs           # content → data/questions.json → index.html
tools/template.html       # 刷题页模板
tools/extract/            # 登录 / 抓取 / 补抓 / 解析导出
tools/classify/           # 分类生成器 + 脱敏模板
data/raw/                 # 原始会话（gitignore，绝不提交）
index.html                # 离线刷题器（构建产物）
```

## 题目格式

每题一个 Markdown，分类由**目录路径**决定。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

```markdown
---
id: go-slice-intersection
type: 手撕代码
difficulty: easy
tags: [切片, map, 交集]
sources: [gemini]
date: 2026-11-12
---

## 题目
go slice 切片取交集

## 回答
...
```

## 隐私说明

- `data/raw/`（原始全量会话）与 `tools/classify/scrub_pii.py`（真实姓名 / 公司映射）**均被 gitignore，绝不提交**。
- 公开前务必运行脱敏脚本，覆盖姓名、简历文件名、公司名、项目名、内网域名 / IP、住址等。
- `content/` 里的示例题目（`example-*`）仅供参考格式，使用前可删除。

## 出处

由个人后端面试题库仓库提炼、泛化而来（原题库见 [yuanhuizang-cloud/backend-interview](https://github.com/yuanhuizang-cloud/backend-interview)）。

## License

[MIT](LICENSE)
