"""Wrap an artifact page fragment into a standalone HTML document for GitHub Pages."""
import sys, re
src, dst, desc = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding='utf-8').read()
m = re.search(r'<title>(.*?)</title>', s); title = m.group(1) if m else 'Report'
body = s.replace(m.group(0), '', 1) if m else s
head_end = body.index('</style>') + len('</style>')
head, rest = body[:head_end], body[head_end:]
out = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       f'<title>{title}</title>\n<meta name="description" content="{desc}">\n' + head + '\n</head>\n<body>\n' + rest + '\n</body>\n</html>\n')
open(dst, 'w', encoding='utf-8').write(out); print('wrapped', dst, len(out) // 1024, 'KB')
