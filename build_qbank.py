# -*- coding: utf-8 -*-
"""Build app/data/qbank.json - the FULL Question Bank as a Q&A reader.

Every question from every set (Rounds 1-4) is emitted in reading order with its
answer shown inline, so the app can present a "next question" flashcard reader
for final revision. Reuses the parsing helpers from build_data.py.
"""
import json, io, sys
if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import build_data as bd

OUT = "app/data/qbank.json"

def qa_for_set(fn):
    """Return an ordered list of {q, a, type, section} for one QB set,
    preserving the original question order within the document."""
    text = bd.load(fn)
    grid = bd.parse_answer_grid(text)
    region = bd.find_answer_region(text)
    ans_blocks = bd.parse_keyed_answers_by_section(region)
    suggested = bd.extract_suggested_prose(region)  # unnumbered fallback paragraphs
    sug_i = 0
    qbody = bd.get_question_body(text)

    tf_blocks = [b["tf"] for b in ans_blocks if b["tf"]]
    letter_blocks = [b["letters"] for b in ans_blocks if b["letters"]]
    prose_blocks = [b["prose"] for b in ans_blocks if b["prose"]]
    tf_i = letter_i = prose_i = 0

    items = []
    for name, body in bd.iter_question_sections(qbody):
        kind, payload = bd.classify_section(body)
        # skip empty instruction "sections" so the answer-block queues stay aligned
        payload_len = len(payload[0]) if kind == "match" else len(payload)
        if payload_len == 0:
            continue
        if kind == "mcq":
            for it in payload:
                letter = grid.get(it["num"])
                ci = "ABCD".find(letter) if letter else -1
                ans = None
                if ci >= 0:
                    ans = f"{letter}. {it['options'][ci]}"
                opts = [f"{'ABCD'[i]}. {o}" for i, o in enumerate(it["options"])]
                items.append({"type": "mcq", "section": name,
                              "q": it["prompt"], "options": opts, "a": ans})
        elif kind == "tf":
            block = tf_blocks[tf_i] if tf_i < len(tf_blocks) else {}
            tf_i += 1
            for it in payload:
                a = block.get(it["num"])
                a_txt = "Benar (True)" if a == "True" else ("Salah (False)" if a == "False" else None)
                items.append({"type": "tf", "section": name,
                              "q": it["prompt"], "a": a_txt})
        elif kind == "match":
            terms, defs = payload
            block = letter_blocks[letter_i] if letter_i < len(letter_blocks) else {}
            letter_i += 1
            for it in terms:
                letter = block.get(it["num"])
                atext = defs.get(letter) if letter else None
                a = f"{letter}. {atext}" if atext else (letter or None)
                items.append({"type": "match", "section": name,
                              "q": f"Padankan: {it['term']}", "a": a})
        else:  # open / structured / rapid-fire
            block = prose_blocks[prose_i] if prose_i < len(prose_blocks) else {}
            prose_i += 1
            block_vals = [block[k] for k in sorted(block)] if block else []
            for pos, it in enumerate(payload):
                a = block.get(it["num"])
                if not a and pos < len(block_vals):
                    a = block_vals[pos]
                if not a and sug_i < len(suggested):
                    a = suggested[sug_i]; sug_i += 1
                items.append({"type": "open", "section": name,
                              "q": it["prompt"], "a": a})
    return items

def main():
    rounds = {}
    for fn, rnd, st in bd.FILES:
        items = qa_for_set(fn)
        rk = str(rnd)
        rounds.setdefault(rk, {"topic": bd.ROUND_META[rnd]["topic"],
                               "title": bd.ROUND_META[rnd]["title"],
                               "sets": []})
        rounds[rk]["sets"].append({"set": st, "items": items})
        answered = sum(1 for it in items if it.get("a"))
        print(f"{fn}: {len(items)} Q ({answered} with answers)")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"rounds": rounds}, f, ensure_ascii=False, indent=1)
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
