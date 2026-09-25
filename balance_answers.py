# -*- coding: utf-8 -*-
"""Rebalance MCQ correct-answer positions across A/B/C/D.

For every 4-option question (type mcq / concept), we reposition the correct
option so that, per round and per category, the correct answers are spread as
evenly as possible across the four slots. Options are reordered together with
their correct index, so correctness is preserved.

Run AFTER build_data.py (which chains gen_mcq). Idempotent.
"""
import json, io, sys, random

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

QUIZ = "app/data/quiz.json"
rng = random.Random(20260428)

def rebalance_group(questions):
    """Assign target correct-positions round-robin (shuffled per cycle) and
    reorder each question's options to place the correct answer there."""
    # Build a balanced sequence of target slots 0..3
    n = len(questions)
    slots = []
    while len(slots) < n:
        cycle = [0, 1, 2, 3]
        rng.shuffle(cycle)
        slots.extend(cycle)
    slots = slots[:n]

    order = list(range(n))
    rng.shuffle(order)  # randomise which question gets which slot

    for qi, target in zip(order, slots):
        q = questions[qi]
        opts = q.get("options")
        ci = q.get("answerIndex")
        if not opts or len(opts) != 4 or ci is None or not (0 <= ci < 4):
            continue
        correct = opts[ci]
        others = [o for i, o in enumerate(opts) if i != ci]
        rng.shuffle(others)
        new = others[:]
        new.insert(target, correct)
        q["options"] = new
        q["answerIndex"] = target
        q["answer"] = "ABCD"[target]

def main():
    d = json.load(open(QUIZ, encoding="utf-8"))
    for rk, r in d["rounds"].items():
        # gather MCQ-type questions grouped so each group is balanced separately
        set_mcqs = [q for s in r["sets"] for q in s["quiz"] if q["type"] == "mcq"]
        extra = r.get("extraMcqs", [])
        concepts = r.get("concepts", [])
        for group in (set_mcqs, extra, concepts):
            if group:
                rebalance_group(group)
    json.dump(d, open(QUIZ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("Rebalanced", QUIZ)

if __name__ == "__main__":
    main()
