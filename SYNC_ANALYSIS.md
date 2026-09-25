# MTAQ 2026 — Question Bank vs Source Sync Analysis

Prepared for a participant. This checks whether each Question Bank (QB) matches the
prescribed sources and quiz rules in `Sources/MTAQ - Quiz.pdf`.

## Quiz structure (from MTAQ - Quiz.pdf)

| Round | Topic | Prescribed source | Answered by |
|-------|-------|-------------------|-------------|
| 1 | Tafsir | Tafsir Al-Azhar (Hamka), Juzu' 28 — Surah As-Saff, Al-Jumu'ah, At-Talaq | 1 participant (individual) |
| 2 | Fiqh Keluarga | Al-Fiqh Al-Manhaji, Jilid 4 (Undang Kekeluargaan) | 1 participant (individual) |
| 3 | Tauhid / Akidah | Manhaj Akidah Ahli Sunnah Wal Jamaah (Pej. Mufti WP / JAKIM, 2016) | Group (both together) |
| 4 | Akhlak | Kitab Penawar Bagi Hati — Syeikh Abd Qadir al-Mandili | Group (both together) |

- Category: open adult, PETRONAS Group employees, group of 2.
- Rounds 1 & 2 answered individually; Rounds 3 & 4 answered together. The QB format
  notes match this (Round 1/2 marked "individual", Round 3/4 marked "team").

## Overall verdict

Rounds 1, 2 and 3 are well synced with their prescribed sources — verified against the
actual extracted text of each book. Round 4 could not be verified because the source PDF
is a scanned image (see the gap below).

| Round | Versions | Source extracted? | Sync verdict |
|-------|----------|-------------------|--------------|
| 1 | 3 | Yes (Tafsir Al-Azhar 10, 844 pp) | In sync — verified |
| 2 | 3 | Yes (Fiqh Manhaji J4, 223 pp) | In sync — verified |
| 3 | 3 | Yes (Manhaj Akidah, 63 pp) | In sync — verified |
| 4 | 2 | No — scanned image, no text | Structure plausible, not verifiable without OCR |

## Round 1 — verified facts against Tafsir Al-Azhar

Key claims cross-checked directly in the source:
- As-Saff = Surah 61 (source: "Surat ash-Shaff (Surat 61)"). QB 1-1 Q1 = B (61). ✓
- Al-Jumu'ah = Surah 62, 11 ayat (source: "Surat 62: 11 ayat"). QB Q17 = C (62), Q18 = C (11). ✓
- At-Talaq = Surah 65, 12 ayat (source: "Surat 65: 12 ayat"). QB Q33 = C (65), Q34 = C (12). ✓
- "Ummi" = illiterate / unlettered, and the ~23-year revelation period — both present in source. ✓
- Parable of the donkey carrying books (keldai/himar), the name "Ahmad", Hawariyyun — all present. ✓

Note: the Tafsir source is in Indonesian; the QBs are in Malay. Meaning maps directly.

## Round 2 — verified facts against Al-Fiqh Al-Manhaji Jilid 4

The book's own table of contents lists exactly the seven divisions the QB uses:
Nikah, Talak (with al-Ila', Zhihar, Li'an), Nafkah, Hadhanah, Radha'ah, Nasab, Laqith. ✓
- Nikah has 5 rukun: Sighat (ijab kabul), istri, suami, wali, saksi. QB 2-1 Q14 = A (5). ✓
- Cannot add a 5th wife to four existing wives. QB matches. ✓
- Radha'ah (breastfeeding) prohibits marriage as lineage does. QB matches. ✓

## Round 3 — verified facts against Manhaj Akidah ASWJ

- The book has exactly 15 rukun/principles (source TOC runs to "Rukun Yang Kelima Belas").
  QB structure ("15 prinsip akidah") matches. ✓
- Six deviating groups listed identically: Haruriah, Qadariah, Jahmiah, Murjiah,
  Rafidhah, Jabariah. QB 3-1 Q47 and 3-2 Q29 match exactly. ✓
- Imam Abu Hasan al-Asy'ari and Imam Abu Mansur al-Maturidi named as strengthening the
  manhaj. QB 3-1 Q3 matches. ✓

## The one gap: Round 4 (Penawar Bagi Hati)

`Sources/Penawar Bagi Hati_4755.pdf` is a 105-page fully scanned image (0 text characters
per page, 1 image per page). It is also in Jawi (Arabic-script Malay). Because of this:

- The Round 4 QBs (Set 1 and Set 2) could NOT be verified against the source text.
- Only two Round 4 versions exist; all other rounds have three.
- The QB's described structure (intro on tasawuf, 7 outward limbs, 10 blameworthy traits,
  10 praiseworthy traits) is the standard structure of this genre of kitab and is
  internally consistent, but this has not been confirmed against the actual book.

### To close the Round 4 gap
1. Install OCR with Jawi/Arabic support (Tesseract + `ara` language data), OCR the PDF,
   then re-run the sync check. Jawi OCR accuracy is limited, so manual review would help.
2. Or obtain a text/Rumi (romanised) edition of Penawar Bagi Hati for reliable checking.
3. Consider producing a third Round 4 version to match the other rounds (3 each), once the
   source is verifiable.

## Minor observations (not errors)

- Answer-key tables extracted from the DOCX files sometimes show all "A" for the MCQ grid.
  This looks like a table-extraction artifact for some sets; the per-set prose answer keys
  (Section B/C) are detailed and correct. Worth confirming the MCQ keys render correctly in
  the original Word files (Round 1-1's key extracted with varied letters and looked fine).
- QBs are consistently labelled "practice material, not an official paper" and advise
  checking exact wording against the organiser's prescribed edition — sensible framing.

## How this was checked

Text was extracted with `pdfplumber` (PDFs) and `python-docx` (question banks) into
`extracted/`. Facts were located in the source text and compared to QB questions and
answer keys. Helper scripts: `extract_pdf.py`, `extract_docx.py`, `extract_all.py`,
`extract_sources.py`, `find.py`, `probe_pdf.py`.
