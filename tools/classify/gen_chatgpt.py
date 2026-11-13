# -*- coding: utf-8 -*-
# 从 ChatGPT 原始 JSON（full_text）提取面试问答，按分类生成 content/**/*.md
# 用法：先抓取 data/raw/chatgpt/all.json，再往下方的 M 列表里加映射条目，最后 python3 tools/classify/gen_chatgpt.py
import json, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, 'data', 'raw', 'chatgpt', 'all.json')
CONTENT = os.path.join(ROOT, 'content')
DATE = datetime.date.today().isoformat()

def clean_q(s):
    s = s.strip()
    s = re.sub(r'\s*(用时|思考了|已思考)[^\n]*$', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def split_turns(text):
    parts = re.split(r'(ChatGPT 说：|你说：|GPT 说：)', text)
    turns = []
    cur = None
    buf = ''
    for p in parts:
        if p in ('你说：', 'ChatGPT 说：', 'GPT 说：'):
            if buf.strip() and cur:
                turns.append((cur, buf.strip()))
            cur = 'user' if p == '你说：' else 'assistant'
            buf = ''
        else:
            buf += p
    if buf.strip() and cur:
        turns.append((cur, buf.strip()))
    return turns

def clean_a(s):
    # 去掉行首的引用标记噪音（如 "nowcoder.com +1"、"api-cdn.nowcoder.com"）
    lines = [l for l in s.split('\n') if not re.match(r'^\s*[\w.-]+\.(com|cn|org|net)\s*(\+\d+)?\s*$', l.strip())]
    return '\n'.join(lines).strip()

# (会话标题子串, 用户问题序号, id, 一级, 二级, 题型, 难度, [tags])
# 示例（把标题换成你自己会话的真实标题，序号为该会话里的第几个用户问题，从 0 开始）：
#   ('某个会话标题', 0, 'go-slice-intersection', '编程语言', 'Go', '手撕代码', 'easy', ['切片', 'map', '交集']),
M = [
]

data = json.load(open(RAW))
conv_cache = {}
for c in data:
    turns = split_turns(c['full_text'])
    conv_cache[c['title']] = turns

def find_conv(title):
    for key in conv_cache:
        if title in key or key in title:
            return conv_cache[key]
    return None

written = 0
missing = []
for title, qi, qid, cat, sub, typ, diff, tags in M:
    turns = find_conv(title)
    if turns is None:
        missing.append(title); continue
    users = [t[1] for t in turns if t[0] == 'user']
    assts = [t[1] for t in turns if t[0] == 'assistant']
    if qi >= len(users):
        missing.append(f'{title}#Q{qi}'); continue
    q = clean_q(users[qi])
    a = clean_a(assts[qi]) if qi < len(assts) else ''
    if not q:
        missing.append(f'{title}#Q{qi}'); continue
    d = os.path.join(CONTENT, cat, sub) if sub else os.path.join(CONTENT, cat)
    os.makedirs(d, exist_ok=True)
    fpath = os.path.join(d, qid + '.md')
    if os.path.exists(fpath):
        continue  # 已存在，跳过（增量更新）
    fm = f"---\nid: {qid}\ntype: {typ}\ndifficulty: {diff}\ntags: [{', '.join(tags)}]\nsources: [chatgpt]\ndate: {DATE}\n---\n\n"
    body = f"## 题目\n{q}\n\n## 回答\n{a}\n"
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(fm + body)
    written += 1

print(f'ChatGPT 生成 {written} 个文件')
if missing:
    print('未匹配:', missing)
