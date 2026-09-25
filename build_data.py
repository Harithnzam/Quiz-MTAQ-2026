"""Parse extracted QB text files into structured JSON for the study app."""
import os, re, json, io, sys, random

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC_DIR = "extracted"
OUT = "app/data/quiz.json"

FILES = [
    ("QB Round 1 - 1.txt", 1, 1), ("QB Round 1 - 2.txt", 1, 2), ("QB Round 1 - 3.txt", 1, 3),
    ("QB Round 2 - 1.txt", 2, 1), ("QB Round 2 - 2.txt", 2, 2), ("QB Round 2 - 3.txt", 2, 3),
    ("QB Round 3 - 1.txt", 3, 1), ("QB Round 3 - 2.txt", 3, 2), ("QB Round 3 - 3.txt", 3, 3),
    ("QB Round 4 - 1.txt", 4, 1), ("QB Round 4 - 2.txt", 4, 2),
]

ROUND_META = {
    1: {"topic": "Tafsir", "title": "Tafsir Al-Azhar, Juzu' 28",
        "source": "Tafsir Al-Azhar (Buya Hamka) - Surah As-Saff, Al-Jumu'ah, At-Talaq",
        "mode": "Individual (1 participant answers)"},
    2: {"topic": "Fiqh Keluarga", "title": "Al-Fiqh Al-Manhaji, Jilid 4",
        "source": "Al-Fiqh Al-Manhaji, Jilid 4 (Hukum Keluarga) - Mazhab Syafi'i",
        "mode": "Individual (1 participant answers)"},
    3: {"topic": "Tauhid / Akidah", "title": "Manhaj Akidah Ahli Sunnah wa al-Jamaah",
        "source": "Manhaj Ahli Sunnah wa al-Jamaah Dalam Akidah (Pej. Mufti WP, 2016)",
        "mode": "Team (both answer together)"},
    4: {"topic": "Akhlak", "title": "Kitab Penawar Bagi Hati",
        "source": "Kitab Penawar Bagi Hati - Syeikh Abd Qadir al-Mandili",
        "mode": "Team (both answer together)"},
}

def load(fn):
    with open(os.path.join(SRC_DIR, fn), encoding="utf-8") as f:
        return f.read()

def parse_answer_grid(text):
    ans = {}
    for line in text.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.split("|")]
        i = 0
        while i + 1 < len(cells):
            n, a = cells[i], cells[i + 1]
            if re.fullmatch(r"\d+", n) and re.fullmatch(r"[A-D]", a):
                ans[int(n)] = a
            i += 2
    return ans

def find_answer_region(text):
    """Return the text from the first 'Answer Key'/'Answer Guide' to the first TABLE marker."""
    m = re.search(r"^(Answer Key|Answer Guide)\s*$", text, re.MULTILINE)
    if not m:
        return ""
    start = m.start()
    tbl = text.find("--- TABLE", start)
    end = tbl if tbl != -1 else len(text)
    return text[start:end]

def parse_keyed_answers_by_section(region):
    """Parse the answer region into per-section answer maps to avoid number
    collisions between Section A/B/C. Returns a list of blocks:
      [{"header": str, "tf": {..}, "letters": {..}, "prose": {..}}]
    in document order. The first block covers answers before any sub-header.
    """
    # Split region into sub-blocks at 'Section X', 'Corrections...', or specific headers.
    lines = region.splitlines()
    blocks = [{"header": "__lead__", "tf": {}, "letters": {}, "prose": {}}]
    for line in lines:
        s = line.strip()
        # sub-header detection
        if re.match(r"^(Section [A-C]\b.*|Corrections for False Statements|"
                    r"Section [A-C]:.*|Answer Key|Answer Guide)$", s):
            blocks.append({"header": s, "tf": {}, "letters": {}, "prose": {}})
            continue
        m = re.match(r"^(\d+)\.\s*(.+)$", s)
        if not m:
            continue
        num, val = int(m.group(1)), m.group(2).strip()
        b = blocks[-1]
        if re.fullmatch(r"(True|False)", val):
            b["tf"][num] = val
        elif re.fullmatch(r"[A-T]", val):
            b["letters"][num] = val
        else:
            b["prose"][num] = val
    return blocks

def merged_maps(blocks):
    """Backwards-compatible flat maps (used for MCQ grid-independent lookups)."""
    tf, letters, prose = {}, {}, {}
    for b in blocks:
        tf.update(b["tf"]); letters.update(b["letters"]); prose.update(b["prose"])
    return tf, letters, prose

QUESTION_SECTION_RE = re.compile(
    r"^Section [A-C]:\s*(?!choose|mark|provide|contains)(.+)$", re.IGNORECASE)

def get_question_body(text):
    """Return text between the first real question section and the Answer region."""
    # Question area starts at first 'Section A:' that is a header (title case topic),
    # not an instruction. We take from first 'Section A:' after 'Instructions'/'How to Use'.
    # Simplest: cut everything from 'Answer Key'/'Answer Guide' onward.
    m = re.search(r"^(Answer Key|Answer Guide)\s*$", text, re.MULTILINE)
    qend = m.start() if m else len(text)
    return text[:qend]

def iter_question_sections(qbody):
    """Yield (section_title, body) for each question section header."""
    heads = []
    for m in re.finditer(r"^Section [A-C]:\s*(.+)$", qbody, re.MULTILINE):
        title = m.group(1).strip()
        # skip instruction-style descriptions
        if re.match(r"(choose|mark|provide|contains|answer)", title, re.IGNORECASE):
            continue
        heads.append((m.start(), m.group(0).strip()))
    heads.append((len(qbody), "__END__"))
    for i in range(len(heads) - 1):
        s, name = heads[i]
        e = heads[i + 1][0]
        if name != "__END__":
            yield name, qbody[s:e]

def extract_mcqs(body):
    items, lines = [], body.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^(\d+)\.\s+(.*)$", lines[i].strip())
        if m and i + 4 < len(lines):
            opts, ok = [], True
            for k in range(1, 5):
                om = re.match(r"^([A-D])\.\s+(.*)$", lines[i + k].strip())
                if om:
                    opts.append(om.group(2))
                else:
                    ok = False; break
            if ok and len(opts) == 4:
                items.append({"num": int(m.group(1)), "prompt": m.group(2), "options": opts})
                i += 5; continue
        i += 1
    return items

def extract_tf(body):
    items = []
    for line in body.splitlines():
        m = re.match(r"^(\d+)\.\s+(.*?)\s+True\s*/\s*False\s*$", line.strip())
        if m:
            items.append({"num": int(m.group(1)), "prompt": m.group(2)})
    return items

def extract_matching(body):
    """Terms 'N. Term: ______' plus the Definitions block A-T."""
    terms = []
    for line in body.splitlines():
        m = re.match(r"^(\d+)\.\s*(.+?):\s*_+\s*$", line.strip())
        if m:
            terms.append({"num": int(m.group(1)), "term": m.group(2).strip()})
    defs = {}
    dm = re.search(r"Definitions\s*(.+)$", body, re.DOTALL)
    if dm:
        for line in dm.group(1).splitlines():
            d = re.match(r"^([A-T])\.\s+(.*\S)\s*$", line.strip())
            if d:
                defs[d.group(1)] = d.group(2)
    return terms, defs

def extract_open(body):
    items, lines = [], body.splitlines()
    for idx, line in enumerate(lines):
        m = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if m:
            prompt = m.group(2)
            if not prompt or re.match(r"^[A-D]\.", prompt) or "____" in prompt:
                continue
            nxt = lines[idx + 1].strip() if idx + 1 < len(lines) else ""
            if re.match(r"^A\.\s", nxt):
                continue
            if prompt.endswith(":") or "____" in prompt:
                continue
            items.append({"num": int(m.group(1)), "prompt": prompt})
    return items

def strip_tag(prompt):
    """Remove a leading '[Tag] ' from a prompt, returning (tag, clean_prompt)."""
    m = re.match(r"^\[([^\]]+)\]\s*(.*)$", prompt)
    if m:
        return m.group(1), m.group(2)
    return None, prompt

def is_short_answer(ans):
    """A concise, factual answer suitable for auto-generated MCQ options."""
    if not ans:
        return False
    a = ans.strip().rstrip(".")
    if len(a) > 60:
        return False
    # avoid answers that are full sentences (too many words)
    if len(a.split()) > 9:
        return False
    return True

def extract_suggested_prose(region):
    """Grab unnumbered suggested-answer paragraphs (fallback for sets whose
    structured answers are prose, not numbered)."""
    paras = []
    started = False
    for line in region.splitlines():
        s = line.strip()
        if re.search(r"Suggested Answer Points|Suggested Points", s, re.IGNORECASE):
            started = True
            continue
        if not started:
            continue
        if not s or s.startswith("Scope") or s.startswith("--- TABLE"):
            continue
        if re.match(r"^Section ", s):
            continue
        # skip numbered lines (already captured) but keep prose
        if re.match(r"^\d+\.\s", s):
            paras.append(re.sub(r"^\d+\.\s*", "", s))
        else:
            paras.append(s)
    return paras

def classify_section(body):
    """Return ('mcq'|'tf'|'match'|'open', payload) for a question section body."""
    mcqs = extract_mcqs(body)
    if mcqs:
        return "mcq", mcqs
    tfs = extract_tf(body)
    if tfs:
        return "tf", tfs
    terms, defs = extract_matching(body)
    if terms and defs:
        return "match", (terms, defs)
    return "open", extract_open(body)

def build_set(fn):
    text = load(fn)
    grid = parse_answer_grid(text)
    region = find_answer_region(text)
    ans_blocks = parse_keyed_answers_by_section(region)
    suggested_prose = extract_suggested_prose(region)
    qbody = get_question_body(text)

    # Question sections in order
    qsections = [(name, body, *classify_section(body))
                 for name, body in iter_question_sections(qbody)]

    # Build ordered queues of answer blocks by the answer type they contain.
    tf_blocks = [b["tf"] for b in ans_blocks if b["tf"]]
    letter_blocks = [b["letters"] for b in ans_blocks if b["letters"]]
    prose_blocks = [b["prose"] for b in ans_blocks if b["prose"]]
    tf_i = letter_i = prose_i = 0

    quiz, review, concept_seeds = [], [], []

    for name, body, kind, payload in qsections:
        if kind == "mcq":
            for it in payload:
                letter = grid.get(it["num"])
                ci = "ABCD".find(letter) if letter else -1
                tag, clean = strip_tag(it["prompt"])
                correct = it["options"][ci] if ci >= 0 else None
                quiz.append({"type": "mcq", "section": name, "tag": tag, "prompt": clean,
                             "options": it["options"], "answerIndex": ci, "answer": letter,
                             "justification": f"Jawapan tepat: {correct}." if correct else None})
        elif kind == "tf":
            block = tf_blocks[tf_i] if tf_i < len(tf_blocks) else {}
            tf_i += 1
            for it in payload:
                tag, clean = strip_tag(it["prompt"])
                a = block.get(it["num"])
                just = ("Pernyataan ini BENAR mengikut sumber." if a == "True"
                        else "Pernyataan ini SALAH mengikut sumber.") if a else None
                quiz.append({"type": "tf", "section": name, "tag": tag, "prompt": clean,
                             "answer": a, "justification": just})
        elif kind == "match":
            terms, defs = payload
            block = letter_blocks[letter_i] if letter_i < len(letter_blocks) else {}
            letter_i += 1
            options = [f"{k}. {v}" for k, v in sorted(defs.items())]
            for it in terms:
                letter = block.get(it["num"])
                atext = defs.get(letter) if letter else None
                quiz.append({"type": "match", "section": name, "tag": None, "prompt": it["term"],
                             "options": options, "answer": letter, "answerText": atext,
                             "justification": f"{it['term']} = {atext}" if atext else None})
        else:  # open
            block = prose_blocks[prose_i] if prose_i < len(prose_blocks) else {}
            prose_i += 1
            for it in payload:
                ans = block.get(it["num"])
                tag, clean = strip_tag(it["prompt"])
                if is_short_answer(ans):
                    concept_seeds.append({"section": name, "tag": tag, "prompt": clean,
                                          "answer": ans.strip().rstrip(".")})
                elif ans:
                    review.append({"section": name, "tag": tag, "prompt": clean, "answer": ans})
                else:
                    review.append({"section": name, "tag": tag, "prompt": clean, "answer": None})
    return quiz, review, suggested_prose, concept_seeds

def dedupe_seeds(seeds):
    """Drop duplicate prompts; keep first."""
    seen, out = set(), []
    for s in seeds:
        key = s["prompt"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out

def answer_shape(ans):
    """Classify an answer so distractors match its shape (plausibility)."""
    a = ans.strip()
    if re.fullmatch(r"\d+", a):
        return "number"
    wc = len(a.split())
    if wc <= 2:
        return "short"
    return "phrase"

def build_concept_mcqs(seeds):
    """Turn short-answer seeds into MCQs with SHAPE-MATCHED distractors so the
    options are plausible (numbers vs numbers, phrases vs phrases)."""
    seeds = dedupe_seeds(seeds)
    # group distinct answers by shape and by section for plausible distractors
    by_shape = {}
    by_section = {}
    for s in seeds:
        if not s["answer"]:
            continue
        by_shape.setdefault(answer_shape(s["answer"]), set()).add(s["answer"])
        by_section.setdefault(s["section"], set()).add(s["answer"])
    items = []
    rng = random.Random(42)  # deterministic build
    for s in seeds:
        correct = s["answer"]
        shape = answer_shape(correct)
        # candidate distractors: same shape first, prefer same section
        same_shape = {a for a in by_shape.get(shape, set()) if a.lower() != correct.lower()}
        same_section = {a for a in by_section.get(s["section"], set())
                        if a.lower() != correct.lower()} & same_shape
        ranked = list(same_section) + [a for a in same_shape if a not in same_section]
        if len(ranked) < 3:
            # fall back to any short answers of same shape across pool
            extra = {a for a in by_shape.get(shape, set()) if a.lower() != correct.lower()}
            ranked = list(dict.fromkeys(list(ranked) + list(extra)))
        if len(ranked) < 3:
            continue  # skip if we cannot make a fair set
        rng.shuffle(ranked)
        distractors = ranked[:3]
        options = distractors + [correct]
        rng.shuffle(options)
        ci = options.index(correct)
        items.append({"type": "concept", "section": s["section"], "tag": s["tag"],
                      "prompt": s["prompt"], "options": options, "answerIndex": ci,
                      "answer": "ABCD"[ci],
                      "justification": f"Jawapan tepat: {correct}."})
    return items

def main():
    rounds = {}
    round_seeds = {}
    for fn, rnd, st in FILES:
        quiz, review, suggested, seeds = build_set(fn)
        rounds.setdefault(str(rnd), {"meta": ROUND_META[rnd], "sets": []})
        rounds[str(rnd)]["sets"].append({"set": st, "quiz": quiz, "review": review,
                                          "suggested": suggested})
        round_seeds.setdefault(str(rnd), []).extend(seeds)
        keyed = sum(1 for q in quiz if q.get("answer"))
        print(f"{fn}: {len(quiz)} gradable ({keyed} keyed), {len(review)} review, {len(seeds)} concept-seed")

    # Build round-level concept MCQ bank and attach category summary
    for rk, r in rounds.items():
        concepts = build_concept_mcqs(round_seeds.get(rk, []))
        r["concepts"] = concepts
        # category counts across all sets + concepts
        counts = {"mcq": 0, "tf": 0, "match": 0, "concept": len(concepts)}
        for s in r["sets"]:
            for q in s["quiz"]:
                counts[q["type"]] = counts.get(q["type"], 0) + 1
        r["categoryCounts"] = counts
        print(f"Round {rk}: concepts={len(concepts)} categories={counts}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"rounds": rounds}, f, ensure_ascii=False, indent=1)
    print("Wrote", OUT)

    # Chain the note-derived MCQ generator so every round reaches >=100 MCQs.
    try:
        import gen_mcq
        print("--- generating note-derived MCQs ---")
        gen_mcq.main()
    except Exception as e:
        print("gen_mcq step skipped:", e)

    # Rebalance correct-answer positions across A/B/C/D.
    try:
        import balance_answers
        print("--- balancing answer positions ---")
        balance_answers.main()
    except Exception as e:
        print("balance step skipped:", e)

if __name__ == "__main__":
    main()
