#!/usr/bin/env python3
import re
from pathlib import Path

SRC = Path('/Users/bino/Downloads/cattaneo/assets/css/styles.css')
BACKUP = SRC.with_suffix('.css.bak')
OUT = SRC.with_suffix('.css.cleaned')

# Match selectors that contain the element 'form' as a standalone token or the class '.form-item'
# We'll check each selector in a selector list (split by comma) for these patterns.
FORM_PAT = re.compile(r'(^|[^a-zA-Z0-9_-])(form)([^a-zA-Z0-9_-]|$)')
FORM_ITEM_PAT = re.compile(r'\.form-item(?![a-zA-Z0-9_-])')

print('Reading', SRC)
text = SRC.read_text()

# Simple state machine to iterate through stylesheet and keep or drop rule blocks
out_lines = []
i = 0
n = len(text)

while i < n:
    # find next '{'
    j = text.find('{', i)
    if j == -1:
        out_lines.append(text[i:])
        break
    # find selector text between i and j
    selector_text = text[i:j].strip()
    # find the full block by scanning braces
    depth = 1
    k = j+1
    while k < n and depth > 0:
        if text[k] == '{':
            depth += 1
        elif text[k] == '}':
            depth -= 1
        k += 1
    block_text = text[i:k]

    # Decide whether to drop based on selector_text
    # Normalize newlines and spaces around selectors
    sel = selector_text.replace('\n', ' ').strip()
    # Split by commas not inside brackets/parentheses - naive but should work for typical CSS
    parts = [p.strip() for p in re.split(r',(?![^()]*\))', sel) if p.strip()]
    drop = False
    for p in parts:
        # If selector contains 'form' as element token or '.form-item' class
        if FORM_ITEM_PAT.search(p) or FORM_PAT.search(p):
            drop = True
            break
    if drop:
        # Skip block
        i = k
        continue
    else:
        out_lines.append(text[i:k])
        i = k

cleaned = ''.join(out_lines)

# Backup original
if not BACKUP.exists():
    SRC.replace(BACKUP)
    # write the original back to SRC from backup
    BACKUP.replace(SRC)
# Write cleaned file
OUT.write_text(cleaned)
print('Wrote cleaned CSS to', OUT)
print('Backup of original at', BACKUP)
