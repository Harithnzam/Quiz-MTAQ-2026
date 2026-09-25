# -*- coding: utf-8 -*-
"""Generate additional fact-based MCQs from the verified notes so every round
has >= 100 MCQ-type questions. Distractors are drawn from sibling note points
in the same round (shape/topic aware) to stay plausible.

Output is written into app/data/quiz.json under each round as `extraMcqs`,
which the app merges into the MCQ category pool.
"""
import json, io, sys, re, random

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

NOTES = "app/data/notes.json"
QUIZ = "app/data/quiz.json"

rng = random.Random(2026)

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def make_definition_mcqs(round_key, sections):
    """Build 'Apakah maksud/definisi X?' questions from 'Term: definition' points,
    using other definitions in the same round as distractors."""
    # reject subjects that are sentence fragments rather than terms
    BAD_SUBJ = re.compile(r"(nya$|terbahagi|difahami|dianjurkan|^Antara|^Sebab|^Bahaya|"
                          r"^Rawatan|^Punca|^Mengapa|^Faedah|^Tanda|^Cara|^Had |^Manfaat|"
                          r"^Hikmah|^Struktur|^Contoh|^Kegunaan|^Kesan|^Tingkat|^Jenis|"
                          r"^Untuk |^Bagi |^Dalam |^Apabila |^Jika |^Selain |^Setiap |"
                          r"^Peliharalah|^Elakkan|^Gunakan|^Kurangkan|^Niatkan|fokus)",
                          re.IGNORECASE)
    pairs = []  # (subject, definition, section_heading)
    for sec in sections:
        for p in sec["points"]:
            m = re.match(r"^(?:\d+\)\s*)?([A-Z][^:]{2,45}):\s*(.+)$", p)
            if m:
                subj = clean(m.group(1))
                definition = clean(m.group(2))
                subj = re.sub(r"\s*\(.*?\)\s*$", "", subj)  # trim trailing bracket
                subj = re.sub(r"\s*\(.*?\)\s*", " ", subj).strip()  # trim inner bracket
                if BAD_SUBJ.search(subj):
                    continue
                # subject should be a compact term/phrase
                if not (2 <= len(definition) <= 170 and 1 <= len(subj.split()) <= 5):
                    continue
                pairs.append((subj, definition, sec["heading"]))
    # dedupe by subject
    seen = set(); uniq = []
    for s, d, h in pairs:
        k = s.lower()
        if k in seen: continue
        seen.add(k); uniq.append((s, d, h))
    defs_pool = [d for _, d, _ in uniq]
    items = []
    for subj, definition, heading in uniq:
        distract = [d for d in defs_pool if d != definition]
        if len(distract) < 3:
            continue
        opts = rng.sample(distract, 3) + [definition]
        rng.shuffle(opts)
        ci = opts.index(definition)
        items.append({
            "type": "mcq", "section": "Nota: " + heading, "tag": "Definisi",
            "prompt": f"Apakah maksud/keterangan bagi: {subj}?",
            "options": opts, "answerIndex": ci, "answer": "ABCD"[ci],
            "justification": f"{subj}: {definition}",
        })
    return items

def first_sentence(text):
    # take up to the first sentence-ending period for a concise fact
    m = re.match(r"^(.+?[.)])(\s|$)", text)
    frag = m.group(1) if m else text
    return clean(frag)

def make_truth_mcqs(round_key, sections):
    """Build 'Manakah pernyataan yang BENAR berkaitan <topic>?' questions.
    correct = a real note fact; distractors = real facts from OTHER topics
    (so they are true-in-general but wrong for this topic's stem)."""
    facts = []  # (heading, statement)
    for sec in sections:
        for p in sec["points"]:
            stmt = clean(p)
            # strip leading 'N)' enumerations
            stmt = re.sub(r"^\d+\)\s*", "", stmt)
            # if the point is a 'Term: definition', convert to a readable fact
            m = re.match(r"^([^:]{3,55}):\s*(.+)$", stmt)
            if m:
                stmt = f"{clean(m.group(1))} - {first_sentence(clean(m.group(2)))}"
            else:
                stmt = first_sentence(stmt)
            if 18 <= len(stmt) <= 200:
                facts.append((sec["heading"], stmt))
    items = []
    if len(facts) < 8:
        return items
    # index facts by heading so distractors come from DIFFERENT headings
    for heading, stmt in facts:
        others = [s for (h, s) in facts if h != heading and s != stmt]
        if len(others) < 3:
            others = [s for (h, s) in facts if s != stmt]
        if len(others) < 3:
            continue
        opts = rng.sample(others, 3) + [stmt]
        rng.shuffle(opts)
        ci = opts.index(stmt)
        topic = re.sub(r"\s*\(.*?\)\s*", " ", heading).strip()
        topic = re.sub(r"^(Kitab \d+ - |Bab \d+ - |Nota: )", "", topic).strip()
        items.append({
            "type": "mcq", "section": "Nota: " + heading, "tag": "Fakta",
            "prompt": f"Manakah pernyataan yang BENAR berkaitan '{topic}'?",
            "options": opts, "answerIndex": ci, "answer": "ABCD"[ci],
            "justification": stmt,
        })
    return items

KEY_TERMS = {
 # round -> list of (term, ...) important vocabulary used for cloze distractors
 "1": ["As-Saff", "Al-Jumu'ah", "At-Talaq", "Ahmad", "Hawariyyun", "ummi", "iddah",
       "Madinah", "keldai", "takwa", "bunyanun marsus", "Musa", "Isa"],
 "2": ["nikah", "talak", "khulu'", "ila'", "zihar", "li'an", "hadhanah", "radha'ah",
       "nasab", "laqith", "mahar", "wali", "iddah", "sunni", "bid'i", "raj'i"],
 "3": ["Sunnah", "Jamaah", "al-Asy'ari", "al-Maturidi", "kasab", "tauqifiyyah",
       "mukjizat", "karamah", "Qadariah", "Jabariah", "Rafidhah", "mutawatir",
       "Ilmu", "Qudrat", "Hayat", "Iradat", "Kalam", "imamah", "fasiq"],
 "4": ["taubat", "khauf", "zuhud", "sabar", "syukur", "ikhlas", "tawakal",
       "mahabbah", "reda", "dengki", "ghibtah", "takbur", "ujub", "riyak",
       "hasad", "namimah", "ghibah", "bakhil"],
}

def make_cloze_mcqs(round_key, sections):
    """Blank out a known key term inside a fact and ask to complete it.
    Distractors are other key terms of the same round."""
    terms = KEY_TERMS.get(round_key, [])
    if len(terms) < 4:
        return []
    items = []
    used = set()
    for sec in sections:
        for p in sec["points"]:
            stmt = re.sub(r"^\d+\)\s*", "", clean(p))
            stmt = first_sentence(stmt)
            if not (25 <= len(stmt) <= 160):
                continue
            # find a key term present in this statement (word-ish match)
            found = None
            for t in terms:
                if re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", stmt, re.IGNORECASE):
                    found = t
                    break
            if not found:
                continue
            key = (sec["heading"], found, stmt[:40])
            if key in used:
                continue
            used.add(key)
            blanked = re.sub(r"(?<!\w)" + re.escape(found) + r"(?!\w)", "______", stmt, count=1, flags=re.IGNORECASE)
            distract = [t for t in terms if t.lower() != found.lower()]
            if len(distract) < 3:
                continue
            opts = rng.sample(distract, 3) + [found]
            rng.shuffle(opts)
            ci = opts.index(found)
            items.append({
                "type": "mcq", "section": "Nota: " + sec["heading"], "tag": "Lengkapkan",
                "prompt": f"Lengkapkan: {blanked}",
                "options": opts, "answerIndex": ci, "answer": "ABCD"[ci],
                "justification": stmt,
            })
    return items

def main():
    notes = json.load(open(NOTES, encoding="utf-8"))
    quiz = json.load(open(QUIZ, encoding="utf-8"))

    notes_by_round = {str(b["round"]): b["sections"] for b in notes["books"]}

    for rk, r in quiz["rounds"].items():
        # count current mcq in the pool
        cur_mcq = sum(1 for s in r["sets"] for q in s["quiz"] if q["type"] == "mcq")
        sections = notes_by_round.get(rk, [])
        gen = (make_definition_mcqs(rk, sections)
               + make_truth_mcqs(rk, sections)
               + make_cloze_mcqs(rk, sections))
        # dedupe generated by prompt
        seen = set(); uniq = []
        for it in gen:
            if it["prompt"].lower() in seen: continue
            seen.add(it["prompt"].lower()); uniq.append(it)
        r["extraMcqs"] = uniq
        # keep the home-screen category counts in sync
        if "categoryCounts" in r:
            r["categoryCounts"]["mcq"] = cur_mcq + len(uniq)
        print(f"Round {rk}: existing MCQ={cur_mcq}, generated={len(uniq)}, total MCQ={cur_mcq + len(uniq)}")

    json.dump(quiz, open(QUIZ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Updated", QUIZ)

if __name__ == "__main__":
    main()
