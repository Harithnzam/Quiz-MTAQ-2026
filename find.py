import sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

fn = sys.argv[1]
pattern = sys.argv[2]
ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 0

with open(fn, encoding="utf-8") as f:
    lines = f.readlines()

rx = re.compile(pattern, re.IGNORECASE)
cur_page = 0
for i, line in enumerate(lines):
    m = re.match(r"===== PAGE (\d+) =====", line)
    if m:
        cur_page = int(m.group(1))
    if rx.search(line):
        print(f"[p{cur_page} L{i+1}] {line.rstrip()}")
        for j in range(1, ctx+1):
            if i+j < len(lines):
                print(f"        {lines[i+j].rstrip()}")
