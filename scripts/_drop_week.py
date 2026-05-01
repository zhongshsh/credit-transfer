"""Drop the leading 'Week' column from the lecture-by-lecture table in topics.md."""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

PATH = r'C:\Users\szhong2\Desktop\CMU\学分置换\discussion\docs\request-2\topics.md'
text = open(PATH, encoding='utf-8').read()

# Header row: "| Week | CMU Lecture (Chpt — Topic) | Coverage | SYSU Evidence ... |"
text = re.sub(
    r'\| Week \| CMU Lecture \(Chpt — Topic\) \| Coverage \| SYSU Evidence',
    '| CMU Lecture (Chpt — Topic) | Coverage | SYSU Evidence',
    text,
)
# Separator row: "|---|---|---|---|" -> "|---|---|---|"
text = re.sub(r'^\|---\|---\|---\|---\|\s*$', '|---|---|---|', text, flags=re.M)
# Body rows that begin with a Week column then a chapter cell.
# Match "| <anything not containing | or **> | **Chpt"
# Use a non-greedy capture of the week cell content.
def strip_week(m):
    return '| **Chpt' + m.group(2)

# Strip leading "| <week-cell> | " before "**Chpt"
text = re.sub(
    r'^\|\s*([^|]+?)\s*\|\s*(\*\*Chpt[^\n]*)$',
    lambda m: '| ' + m.group(2),
    text,
    flags=re.M,
)

open(PATH, 'w', encoding='utf-8', newline='\n').write(text)
print('done')
