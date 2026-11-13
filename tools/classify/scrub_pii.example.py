# -*- coding: utf-8 -*-
# 脱敏模板：把 content/**/*.md 里的个人/身份信息替换为通用词
# 使用：cp scrub_pii.example.py scrub_pii.py，然后把你自己的映射填进 REPLACEMENTS，再 python3 scrub_pii.py
# 注意：scrub_pii.py 含真实 PII 映射，已被 gitignore，绝不提交。
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTENT = os.path.join(ROOT, 'content')

# 顺序敏感的替换表（长的在前，避免部分匹配）。
# 每条 (原始值, 替换值)，示例（请替换成你自己的信息）：
#   ('张三简历-高级后端.pdf', '简历.pdf'),
#   ('张三', '我'),
#   ('某科技有限公司', '某公司'),
REPLACEMENTS = [
]

changed_files = 0
total_changes = 0

for dirpath, _, filenames in os.walk(CONTENT):
    for fn in filenames:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(dirpath, fn)
        text = open(p, encoding='utf-8').read()
        new = text
        n = 0
        for a, b in REPLACEMENTS:
            cnt = new.count(a)
            if cnt:
                new = new.replace(a, b)
                n += cnt
        if new != text:
            open(p, 'w', encoding='utf-8').write(new)
            changed_files += 1
            total_changes += n
            print(f'  {os.path.relpath(p, CONTENT)}: {n} 处')

print(f'\n脱敏完成：{changed_files} 个文件，{total_changes} 处替换')
