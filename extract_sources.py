import os
import pdfplumber

os.makedirs("extracted", exist_ok=True)

sources = {
    "Tafsir Al-Azhar 10.pdf": "src_tafsir_azhar_10.txt",
    "Fikih-Manhaji-Madzhab-Imam-Syafii-Jilid-4-EBS-1769434531528.pdf": "src_fiqh_manhaji_j4.txt",
    "Manhaj_Ahli_Sunnah_Wal_Jamaah_Dalam_Akidah.pdf": "src_manhaj_akidah.txt",
    "Penawar Bagi Hati_4755.pdf": "src_penawar_hati.txt",
}

for fn, out in sources.items():
    path = os.path.join("Sources", fn)
    try:
        with pdfplumber.open(path) as pdf:
            n = len(pdf.pages)
            with open("extracted/" + out, "w", encoding="utf-8") as f:
                for i, page in enumerate(pdf.pages):
                    txt = page.extract_text() or ""
                    f.write(f"\n===== PAGE {i+1} =====\n{txt}\n")
            print(f"Wrote {out} ({n} pages)")
    except Exception as e:
        print(f"FAILED {fn}: {e}")

print("DONE SOURCES")
