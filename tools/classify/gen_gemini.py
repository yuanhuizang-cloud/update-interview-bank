# -*- coding: utf-8 -*-
# 从 Gemini 原始 JSON 提取面试问答，按分类生成 content/**/*.md
# 用法：先抓取 data/raw/gemini/all.json，再往下方的 M 列表里加映射条目，最后 python3 tools/classify/gen_gemini.py
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, 'data', 'raw', 'gemini', 'all.json')
CONTENT = os.path.join(ROOT, 'content')
DATE = datetime.date.today().isoformat()

def clean_q(s):
    return re.sub(r'^\s*(你说|You said|您说)\s*[:：]?\s*', '', s).strip()

# 每个条目：(会话标题, 用户问题序号 q_index, id, 一级, 二级, 题型, 难度, [tags])
# 示例（把标题换成你自己会话的真实标题，序号为该会话里的第几个用户问题，从 0 开始）：
#   ('某个会话标题', 0, 'go-slice-intersection', '编程语言', 'Go', '手撕代码', 'easy', ['切片', 'map', '交集']),
M = [
]

data = json.load(open(RAW))
by_title = {}
for c in data:
    by_title.setdefault(c['title'], c)

def find_conv(title):
    for key in by_title:
        if title in key or key in title:
            return by_title[key]
    return None

written = 0
missing = []
for title, qi, qid, cat, sub, typ, diff, tags in M:
    conv = find_conv(title)
    if not conv:
        missing.append(title); continue
    users = [m['text'] for m in conv['messages'] if m['role'] == 'user']
    assts = [m['text'] for m in conv['messages'] if m['role'] == 'assistant']
    if qi >= len(users):
        missing.append(f'{title}#Q{qi}'); continue
    q = clean_q(users[qi])
    a = assts[qi].strip() if qi < len(assts) else ''
    if not q:
        missing.append(f'{title}#Q{qi}'); continue
    d = os.path.join(CONTENT, cat, sub) if sub else os.path.join(CONTENT, cat)
    os.makedirs(d, exist_ok=True)
    fpath = os.path.join(d, qid + '.md')
    if os.path.exists(fpath):
        continue  # 已存在，跳过（增量更新）
    fm = f"---\nid: {qid}\ntype: {typ}\ndifficulty: {diff}\ntags: [{', '.join(tags)}]\nsources: [gemini]\ndate: {DATE}\n---\n\n"
    body = f"## 题目\n{q}\n\n## 回答\n{a}\n"
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(fm + body)
    written += 1

print(f'Gemini 生成 {written} 个文件')
if missing:
    print('未匹配:', missing)
