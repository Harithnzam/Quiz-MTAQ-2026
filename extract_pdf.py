import sys
import pdfplumber

path = sys.argv[1]
with pdfplumber.open(path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        print(f"\n===== PAGE {i+1} =====")
        print(text)
