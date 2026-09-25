import os, io, sys
from docx import Document
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

parts = [
    ("Sources/Penawar_Bagi_Hati_Part 1.docx", "extracted/penawar_rumi_1.txt"),
    ("Sources/Penawar_Bagi_Hati_Part 2.docx", "extracted/penawar_rumi_2.txt"),
    ("Sources/Penawar_Bagi_Hati_Part 3.docx", "extracted/penawar_rumi_3.txt"),
]
for src, out in parts:
    doc = Document(src)
    lines = [p.text for p in doc.paragraphs if p.text.strip()]
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out} ({len(lines)} paras)")
