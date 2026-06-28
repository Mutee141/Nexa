from pathlib import Path
import re

path = Path('templates/dashboard/home.html')
text = path.read_text(encoding='utf-8')
pattern = re.compile(r'{%\s*(\w+)(?:\s+([^%]*?))?\s*%}')
stack = []
for m in pattern.finditer(text):
    cmd = m.group(1)
    arg = (m.group(2) or '').strip()
    line = text.count('\n', 0, m.start()) + 1
    print(f'{line}: {cmd} {arg!r}')
    if cmd in ('if', 'for', 'with', 'block'):
        stack.append((cmd, line, arg))
    elif cmd in ('endif', 'endfor', 'endwith', 'endblock'):
        if not stack:
            print('  UNMATCHED', cmd, 'at line', line)
        else:
            opening = stack.pop()
            print('  MATCHES', opening)
print('\nRemaining stack:', stack)
