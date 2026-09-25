/* ============================================================
   MTAQ 2026 Study App
   Vanilla JS, data-driven, no build step.
   ============================================================ */

const state = {
  quiz: null,
  notes: null,
  view: "home",
  session: null,
  settings: loadSettings(),
};

const ROUND_COLORS = { 1: "r1", 2: "r2", 3: "r3", 4: "r4" };
const ROUND_ICONS = { 1: "📖", 2: "⚖️", 3: "🕌", 4: "💠" };

const CATS = {
  mcq: { label: "Aneka Pilihan", desc: "Soalan MCQ 4 pilihan", ico: "🔘" },
  tf: { label: "Betul / Salah", desc: "Nilai pernyataan", ico: "✓✗" },
  match: { label: "Padanan", desc: "Padan istilah & definisi", ico: "🔗" },
  concept: { label: "Konsep", desc: "Fakta pantas (pilih jawapan)", ico: "⚡" },
  select: { label: "Pilih Semua", desc: "Pilih semua jawapan betul", ico: "☑️" },
};

const $ = (sel, root = document) => root.querySelector(sel);
const app = () => document.getElementById("app");

const POINTS_PER_CORRECT = 10;
function streakBonus(streak) {
  // small escalating bonus for consecutive correct answers
  if (streak >= 5) return 5;
  if (streak >= 3) return 3;
  return 0;
}
function awardPoints(s, correct) {
  if (correct) {
    s.streak++;
    s.bestStreak = Math.max(s.bestStreak, s.streak);
    const gained = POINTS_PER_CORRECT + streakBonus(s.streak);
    s.points += gained;
    return gained;
  }
  s.streak = 0;
  return 0;
}
function statBar(s) {
  return `<span>⭐ <b>${s.points}</b> mata</span>
    <span>Betul <b>${s.correct}</b></span>
    <span class="miss">Salah <b class="miss">${s.records.filter((r) => !r.correct).length}</b></span>`;
}

/* ---------- settings persistence ---------- */
function loadSettings() {
  try {
    return Object.assign(
      { instantReveal: true },
      JSON.parse(localStorage.getItem("mtaq.settings") || "{}")
    );
  } catch {
    return { instantReveal: true };
  }
}
function saveSettings() {
  localStorage.setItem("mtaq.settings", JSON.stringify(state.settings));
}

/* ---------- data ---------- */
async function loadData() {
  const [q, n, sel] = await Promise.all([
    fetch("data/quiz.json").then((r) => r.json()),
    fetch("data/notes.json").then((r) => r.json()),
    fetch("data/select.json").then((r) => r.json()).catch(() => ({ rounds: {} })),
  ]);
  state.quiz = q;
  state.notes = n;
  state.select = sel;
}

/* pool of all playable questions for a round, by category */
function roundPool(round) {
  const r = state.quiz.rounds[round];
  const pool = { mcq: [], tf: [], match: [], concept: [], select: [] };
  r.sets.forEach((s) => s.quiz.forEach((q) => pool[q.type] && pool[q.type].push(q)));
  (r.extraMcqs || []).forEach((q) => pool.mcq.push(q)); // note-derived MCQs
  (r.concepts || []).forEach((q) => pool.concept.push(q));
  const selItems = (state.select?.rounds?.[round]) || [];
  selItems.forEach((q) => pool.select.push(Object.assign({ type: "select" }, q)));
  return pool;
}

/* ---------- navigation ---------- */
function setView(v) {
  state.view = v;
  state.session = null;
  document.querySelectorAll(".tab").forEach((t) =>
    t.classList.toggle("active", t.dataset.view === v)
  );
  if (v === "home") renderHome();
  else if (v === "quiz") renderRoundPicker("quiz");
  else if (v === "notes") renderNotes();
}

/* ---------- HOME ---------- */
function renderHome() {
  const rounds = state.quiz.rounds;
  const roundCards = Object.keys(rounds)
    .sort()
    .map((rk) => {
      const m = rounds[rk].meta;
      const c = rounds[rk].categoryCounts;
      const total = c.mcq + c.tf + c.match + c.concept;
      return `
      <div class="card ${ROUND_COLORS[rk]}" data-action="round" data-round="${rk}" tabindex="0" role="button">
        <div class="icon">${ROUND_ICONS[rk]}</div>
        <div class="kicker">ROUND ${rk} · ${esc(m.topic)}</div>
        <div class="ttl">${esc(m.title)}</div>
        <div class="desc">${total} soalan interaktif</div>
        <div class="chips">
          <span class="chip">${c.mcq} MCQ</span>
          <span class="chip">${c.tf} B/S</span>
          ${c.match ? `<span class="chip">${c.match} Padanan</span>` : ""}
          <span class="chip">${c.concept} Konsep</span>
        </div>
      </div>`;
    })
    .join("");

  const noteCards = state.notes.books
    .map(
      (b) => `
      <div class="card ${ROUND_COLORS[b.round]}" data-action="notebook" data-round="${b.round}" tabindex="0" role="button">
        <div class="icon">${ROUND_ICONS[b.round]}</div>
        <div class="kicker">ROUND ${b.round} · ${esc(b.topic)}</div>
        <div class="ttl">${esc(b.title)}</div>
        <div class="desc">${esc(b.scope)}</div>
        <div class="chips"><span class="chip mode">${b.verified ? "Disahkan dgn sumber" : "Nota dari QB"}</span></div>
      </div>`
    )
    .join("");

  render(`
    <div class="page-head">
      <div class="eyebrow">Selamat berlatih</div>
      <h1>Bersedia untuk MTAQ 2026</h1>
      <p>Kuiz interaktif setiap round dan nota ringkas setiap buku sumber — semuanya di satu tempat.</p>
    </div>

    <div class="section-title"><span class="bar"></span><h2>Kuiz mengikut Round</h2>
      <span class="hint">Pilih kategori & mod jawapan sebelum mula</span></div>
    <div class="grid">${roundCards}</div>

    <div class="section-title"><span class="bar"></span><h2>Nota Buku Sumber</h2>
      <span class="hint">Baca sebelum bertanding</span></div>
    <div class="grid">${noteCards}</div>
  `);
}

/* ---------- ROUND PICKER (quiz tab entry) ---------- */
function renderRoundPicker() {
  const rounds = state.quiz.rounds;
  const cards = Object.keys(rounds)
    .sort()
    .map((rk) => {
      const m = rounds[rk].meta;
      return `<div class="card ${ROUND_COLORS[rk]}" data-action="round" data-round="${rk}" tabindex="0" role="button">
        <div class="icon">${ROUND_ICONS[rk]}</div>
        <div class="kicker">ROUND ${rk}</div>
        <div class="ttl">${esc(m.topic)}</div>
        <div class="desc">${esc(m.title)}</div>
      </div>`;
    })
    .join("");
  render(`
    <div class="page-head"><h1>Pilih Round</h1><p>Setiap round berdasarkan satu buku sumber.</p></div>
    <div class="grid">${cards}</div>
  `);
}

/* ---------- ROUND DETAIL: category + mode + start ---------- */
function renderRoundDetail(round) {
  const r = state.quiz.rounds[round];
  const pool = roundPool(round);
  const sel = state.selectedCats || defaultCats(pool);
  state.selectedCats = sel;

  const catCards = Object.keys(CATS)
    .filter((k) => pool[k].length > 0)
    .map((k) => {
      const on = sel.has(k);
      return `<button class="cat ${on ? "on" : ""}" data-action="togglecat" data-cat="${k}">
        <span class="cat-ico">${CATS[k].ico}</span>
        <span class="cat-meta"><b>${CATS[k].label}</b><span>${pool[k].length} soalan</span></span>
        <span class="check"></span>
      </button>`;
    })
    .join("");

  const selCount = countSelected(pool, sel);
  const instant = state.settings.instantReveal;

  render(`
    <button class="back" data-action="quiztab">← Semua round</button>
    <div class="page-head">
      <div class="eyebrow">Round ${round} · ${esc(r.meta.topic)}</div>
      <h1>${esc(r.meta.title)}</h1>
      <p>${esc(r.meta.source)}</p>
      <div class="chips" style="margin-top:10px"><span class="chip">${esc(r.meta.mode)}</span></div>
    </div>

    <div class="section-title"><span class="bar"></span><h2>1 · Pilih kategori soalan</h2></div>
    <div class="cat-grid">${catCards}</div>

    <div class="section-title"><span class="bar"></span><h2>2 · Mod jawapan</h2></div>
    <div class="panel">
      <div class="field">
        <div class="label">
          <b>Papar jawapan serta-merta</b>
          <span>${instant
            ? "Jawapan & penjelasan dipaparkan selepas setiap soalan."
            : "Ringkasan jawapan & penjelasan dipaparkan di akhir kuiz."}</span>
        </div>
        <label class="switch">
          <input type="checkbox" id="revealToggle" ${instant ? "checked" : ""} />
          <span class="slider"></span>
        </label>
      </div>
    </div>

    <div class="section-title"><span class="bar"></span><h2>3 · Bilangan soalan</h2></div>
    <div class="panel">
      <div class="field">
        <div class="label"><b>Panjang sesi</b><span>Soalan dipilih rawak daripada kategori.</span></div>
        <div class="segmented" id="lenSeg">
          ${[10, 20, 30, 0]
            .map(
              (n) =>
                `<button data-len="${n}" class="${(state.sessionLen ?? 20) === n ? "active" : ""}">${
                  n === 0 ? "Semua" : n
                }</button>`
            )
            .join("")}
        </div>
      </div>
    </div>

    <p class="mini" style="margin-top:14px;color:var(--muted)">
      💯 Pemarkahan: ${POINTS_PER_CORRECT} mata setiap jawapan betul, dengan bonus streak (+3 selepas 3 betul berturut, +5 selepas 5).
    </p>

    <div class="runner-actions" style="margin-top:20px">
      <button class="btn secondary" data-action="review" data-round="${round}">📝 Soalan struktur</button>
      <div class="spacer"></div>
      <button class="btn lg" id="startBtn" data-action="start" data-round="${round}" ${
    selCount ? "" : "disabled"
  }>Mula Kuiz · <b id="qCount">${sessionSize(selCount)}</b> soalan</button>
    </div>
  `);

  $("#revealToggle").addEventListener("change", (e) => {
    state.settings.instantReveal = e.target.checked;
    saveSettings();
    renderRoundDetail(round); // refresh description
  });
  $("#lenSeg").addEventListener("click", (e) => {
    const b = e.target.closest("[data-len]");
    if (!b) return;
    state.sessionLen = parseInt(b.dataset.len, 10);
    renderRoundDetail(round);
  });
}

function defaultCats(pool) {
  return new Set(Object.keys(CATS).filter((k) => pool[k].length > 0));
}
function countSelected(pool, sel) {
  return [...sel].reduce((a, k) => a + pool[k].length, 0);
}
function sessionSize(available) {
  const len = state.sessionLen ?? 20;
  if (len === 0) return available;
  return Math.min(len, available);
}

/* continued in part 2 ... */

/* ---------- QUIZ SESSION ---------- */
function shuffle(arr) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function startSession(round) {
  const pool = roundPool(round);
  const sel = state.selectedCats || defaultCats(pool);
  let items = [];
  [...sel].forEach((k) => (items = items.concat(pool[k])));
  items = shuffle(items);
  const size = sessionSize(items.length);
  items = items.slice(0, size);
  // clone select-type items so their shuffled option cache is fresh each session
  items = items.map((q) => (q.type === "select" ? Object.assign({}, q, { _opts: null, _correctSet: null }) : q));

  state.session = {
    round,
    items,
    idx: 0,
    correct: 0,
    points: 0,
    streak: 0,
    bestStreak: 0,
    instant: state.settings.instantReveal,
    records: [], // {q, chosen, correct:bool, correctLabel}
    answered: false,
  };
  renderQuestion();
}

function buildSelectOptions(q) {
  // combine correct + distractors, shuffle once and cache on the question
  if (!q._opts) {
    const opts = shuffle(q.correct.concat(q.distractors));
    q._opts = opts;
    q._correctSet = new Set(q.correct.map((x) => x.toLowerCase()));
  }
  return q._opts;
}

function optionsMarkup(q) {
  if (q.type === "tf") {
    return `<div class="options">
      <button class="opt" data-choice="True"><span class="letter">B</span><span>Benar (True)</span><span class="mark"></span></button>
      <button class="opt" data-choice="False"><span class="letter">S</span><span>Salah (False)</span><span class="mark"></span></button>
    </div>`;
  }
  if (q.type === "select") {
    const opts = buildSelectOptions(q);
    return `<div class="options" id="selOpts">${opts
      .map(
        (o, i) => `<button class="opt select" data-sel="${i}">
          <span class="letter">☐</span><span>${esc(o)}</span><span class="mark"></span>
        </button>`
      )
      .join("")}</div>
      <div class="row" style="margin-top:14px"><button class="btn secondary" id="submitSel">Sahkan pilihan</button></div>`;
  }
  return `<div class="options">${q.options
    .map((opt, i) => {
      const letter = q.type === "match" ? opt.slice(0, 1) : "ABCD"[i];
      const label = q.type === "match" ? opt.slice(3) : opt;
      const choice = q.type === "match" ? letter : String(i);
      return `<button class="opt" data-choice="${choice}">
        <span class="letter">${letter}</span><span>${esc(label)}</span><span class="mark"></span>
      </button>`;
    })
    .join("")}</div>`;
}

function correctInfo(q) {
  if (q.type === "tf") return { key: q.answer, label: q.answer === "True" ? "Benar (True)" : "Salah (False)" };
  if (q.type === "match") return { key: q.answer, label: `${q.answer}. ${q.answerText || ""}` };
  // mcq / concept
  return { key: String(q.answerIndex), label: q.options[q.answerIndex] };
}

function renderQuestion() {
  const s = state.session;
  const q = s.items[s.idx];
  const total = s.items.length;
  const pct = Math.round((s.idx / total) * 100);

  render(`
    <button class="back" data-action="exitquiz" data-round="${s.round}">← Keluar</button>
    <div class="runner-top">
      <span class="meta">Round ${s.round} · Soalan ${s.idx + 1}/${total}</span>
      <span class="stat">${statBar(s)}</span>
    </div>
    <div class="progress-wrap"><div class="progress-bar" style="width:${pct}%"></div></div>
    <div class="qcard">
      <div class="qtags">
        <span class="badge type">${esc(CATS[q.type]?.label || q.type)}</span>
        ${q.tag ? `<span class="badge tag">${esc(q.tag)}</span>` : ""}
      </div>
      <div class="qprompt">${esc(q.prompt)}</div>
      ${optionsMarkup(q)}
      <div id="fb"></div>
      <div class="runner-actions">
        <div class="spacer"></div>
        <button class="btn" id="nextBtn" disabled>${
          s.idx + 1 < total ? "Seterusnya →" : "Lihat keputusan"
        }</button>
      </div>
    </div>
  `);

  s.answered = false;

  if (q.type === "select") {
    const picked = new Set();
    document.querySelectorAll(".opt.select").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (s.answered) return;
        const i = btn.dataset.sel;
        if (picked.has(i)) { picked.delete(i); btn.classList.remove("on-pick"); btn.querySelector(".letter").textContent = "☐"; }
        else { picked.add(i); btn.classList.add("on-pick"); btn.querySelector(".letter").textContent = "☑"; }
      });
    });
    $("#submitSel").addEventListener("click", () => handleSelectSubmit(picked));
  } else {
    document.querySelectorAll(".opt").forEach((btn) =>
      btn.addEventListener("click", () => handleAnswer(btn))
    );
  }

  $("#nextBtn").addEventListener("click", nextQuestion);

  // keyboard: 1-4 / A-D / B-S choose; Enter next
  document.onkeydown = (e) => {
    if (s.answered && e.key === "Enter") return nextQuestion();
    if (s.answered || q.type === "select") return;
    const opts = [...document.querySelectorAll(".opt")];
    const k = e.key.toLowerCase();
    const map = { a: 0, "1": 0, c: 2, "3": 2, d: 3, "4": 3 };
    if (q.type === "tf") {
      if (k === "b" || k === "1") opts[0]?.click();
      if (k === "s" || k === "2") opts[1]?.click();
    } else {
      const mm = Object.assign({ b: 1, "2": 1 }, map);
      if (k in mm && opts[mm[k]]) opts[mm[k]].click();
    }
  };
}

function handleSelectSubmit(picked) {
  const s = state.session;
  if (s.answered) return;
  s.answered = true;
  const q = s.items[s.idx];
  const opts = q._opts;
  const correctSet = q._correctSet;

  let allRight = true;
  document.querySelectorAll(".opt.select").forEach((b) => {
    b.disabled = true;
    const i = b.dataset.sel;
    const isCorrectOpt = correctSet.has(opts[i].toLowerCase());
    const wasPicked = picked.has(i);
    if (isCorrectOpt) { b.classList.add("correct"); b.querySelector(".mark").textContent = wasPicked ? "✓" : "＋"; if (!wasPicked) allRight = false; }
    else if (wasPicked) { b.classList.add("wrong"); b.querySelector(".mark").textContent = "✗"; allRight = false; }
  });
  const submitBtn = $("#submitSel");
  if (submitBtn) submitBtn.style.display = "none";

  if (allRight) s.correct++;
  const gained = awardPoints(s, allRight);
  s.records.push({
    prompt: q.prompt, tag: q.tag, type: q.type,
    correct: allRight, correctLabel: q.correct.join(", "),
    justification: q.justification,
  });
  const statEl = $(".runner-top .stat");
  if (statEl) statEl.innerHTML = statBar(s);

  if (s.instant) {
    $("#fb").innerHTML = `
      <div class="feedback ${allRight ? "good" : "bad"}">
        <span class="fi">${allRight ? "✅" : "❌"}</span>
        <div>
          <div><strong>${allRight ? `Semua betul! +${gained} mata` : "Kurang tepat."}</strong>
            ${allRight ? "" : ` Jawapan penuh: <strong>${esc(q.correct.join(", "))}</strong>`}</div>
          ${q.justification ? `<div class="just">${esc(q.justification)}</div>` : ""}
        </div>
      </div>`;
  }
  $("#nextBtn").disabled = false;
  $("#nextBtn").focus();
}

function handleAnswer(btn) {
  const s = state.session;
  if (s.answered) return;
  s.answered = true;
  const q = s.items[s.idx];
  const info = correctInfo(q);
  const chosen = btn.dataset.choice;
  const isCorrect = chosen === info.key;

  // mark options
  document.querySelectorAll(".opt").forEach((b) => {
    b.disabled = true;
    const c = b.dataset.choice;
    if (c === info.key) { b.classList.add("correct"); b.querySelector(".mark").textContent = "✓"; }
    else if (b === btn) { b.classList.add("wrong"); b.querySelector(".mark").textContent = "✗"; }
  });

  if (isCorrect) s.correct++;
  const gained = awardPoints(s, isCorrect);
  s.records.push({
    prompt: q.prompt, tag: q.tag, type: q.type,
    correct: isCorrect, correctLabel: info.label,
    justification: q.justification,
  });

  // update live tally
  const statEl = $(".runner-top .stat");
  if (statEl) statEl.innerHTML = statBar(s);

  if (s.instant) {
    $("#fb").innerHTML = `
      <div class="feedback ${isCorrect ? "good" : "bad"}">
        <span class="fi">${isCorrect ? "✅" : "❌"}</span>
        <div>
          <div><strong>${isCorrect ? `Betul! +${gained} mata` : "Kurang tepat."}</strong>
            ${isCorrect ? (s.streak >= 3 ? ` 🔥 streak ${s.streak}` : "") : ` Jawapan: <strong>${esc(info.label)}</strong>`}</div>
          ${q.justification ? `<div class="just">${esc(q.justification)}</div>` : ""}
        </div>
      </div>`;
  }
  $("#nextBtn").disabled = false;
  $("#nextBtn").focus();
}

function nextQuestion() {
  const s = state.session;
  s.idx++;
  if (s.idx >= s.items.length) renderResult();
  else renderQuestion();
}

function renderResult() {
  const s = state.session;
  document.onkeydown = null;
  const total = s.items.length;
  const pct = total ? Math.round((s.correct / total) * 100) : 0;
  const grade = pct >= 85 ? "Cemerlang" : pct >= 70 ? "Baik" : pct >= 50 ? "Sederhana" : "Perlu ulang kaji";
  const msg =
    pct >= 85 ? "Anda sangat bersedia — teruskan!" :
    pct >= 70 ? "Hampir sampai. Ulang bahagian yang tersasar." :
    pct >= 50 ? "Fokus pada kategori yang lemah." :
    "Baca nota buku sumber, kemudian cuba lagi.";

  // In end-mode, show every question's answer; in instant-mode, show only missed.
  const toShow = s.instant ? s.records.filter((r) => !r.correct) : s.records;
  const reviewHtml = toShow.length
    ? `<div class="section-title"><span class="bar"></span><h2>${
        s.instant ? "Soalan yang tersasar" : "Semakan jawapan"
      }</h2></div>
       <div class="review-list">${toShow
         .map(
           (r) => `<div class="review-item ${r.correct ? "hit" : "miss"}">
             <div class="q">${r.tag ? `<span class="badge tag">${esc(r.tag)}</span> ` : ""}${esc(r.prompt)}</div>
             <div class="a"><span class="lbl">Jawapan</span>${esc(r.correctLabel)}</div>
             ${r.justification ? `<div class="a" style="margin-top:4px;color:var(--muted)">${esc(r.justification)}</div>` : ""}
           </div>`
         )
         .join("")}</div>`
    : `<p class="empty">🎉 Semua jawapan betul!</p>`;

  const maxPoints = total * POINTS_PER_CORRECT;
  render(`
    <div class="result">
      <div class="grade">Round ${s.round} · ${grade}</div>
      <div class="ring-wrap"><div class="donut" style="--p:${pct}"><div class="inner"><div class="pct">${pct}%</div></div></div></div>
      <div class="score">${s.correct} / ${total} betul</div>
      <div class="scoreboard">
        <div class="sb"><div class="sb-num">${s.points}</div><div class="sb-lbl">Mata diperoleh</div></div>
        <div class="sb"><div class="sb-num">${s.bestStreak}🔥</div><div class="sb-lbl">Streak terbaik</div></div>
        <div class="sb"><div class="sb-num">${maxPoints}</div><div class="sb-lbl">Mata maksimum</div></div>
      </div>
      <div class="msg">${msg}</div>
      <div class="row" style="justify-content:center">
        <button class="btn" data-action="start" data-round="${s.round}">↻ Cuba lagi</button>
        <button class="btn secondary" data-action="round" data-round="${s.round}">Ubah tetapan</button>
      </div>
    </div>
    ${reviewHtml}
  `);
  // animate donut
  requestAnimationFrame(() => {
    const d = $(".donut");
    if (d) d.style.setProperty("--p", pct);
  });
}

/* continued in part 3 ... */

/* ---------- REVIEW: structured questions as flashcards ---------- */
function renderReview(round) {
  const r = state.quiz.rounds[round];
  const cards = [];
  r.sets.forEach((s) => {
    s.review.forEach((rv) => {
      if (rv.prompt) cards.push(rv);
    });
  });

  const list = cards.length
    ? cards
        .map(
          (rv, i) => `
        <div class="review-item" data-flip="${i}">
          <div class="q">${rv.tag ? `<span class="badge tag">${esc(rv.tag)}</span> ` : ""}${esc(rv.prompt)}</div>
          <div class="a" id="ans-${i}" style="display:none">
            <span class="lbl">Cadangan</span>${rv.answer ? esc(rv.answer) : "Lihat nota buku sumber."}
          </div>
          <button class="btn ghost" style="margin-top:10px" data-action="flip" data-idx="${i}">Tunjuk jawapan</button>
        </div>`
        )
        .join("")
    : `<p class="empty">Tiada soalan struktur untuk round ini.</p>`;

  render(`
    <button class="back" data-action="round" data-round="${round}">← Kembali</button>
    <div class="page-head">
      <div class="eyebrow">Round ${round} · Latihan lisan</div>
      <h1>Soalan Struktur</h1>
      <p>Soalan terbuka untuk latihan lisan berpasangan. Cuba jawab dahulu, kemudian dedah cadangan jawapan.</p>
    </div>
    <div class="review-list">${list}</div>
  `);
}

/* ---------- NOTES ---------- */
function renderNotes() {
  const cards = state.notes.books
    .map(
      (b) => `<div class="card ${ROUND_COLORS[b.round]}" data-action="notebook" data-round="${b.round}" tabindex="0" role="button">
        <div class="icon">${ROUND_ICONS[b.round]}</div>
        <div class="kicker">ROUND ${b.round} · ${esc(b.topic)}</div>
        <div class="ttl">${esc(b.title)}</div>
        <div class="desc">${esc(b.scope)}</div>
      </div>`
    )
    .join("");
  render(`
    <div class="page-head"><h1>Nota Buku Sumber</h1><p>Ringkasan penting untuk persediaan setiap round.</p></div>
    <div class="grid">${cards}</div>
  `);
}

function renderNoteBook(round) {
  const b = state.notes.books.find((x) => String(x.round) === String(round));
  if (!b) return renderNotes();
  const secs = b.sections
    .map(
      (sec) => `<div class="note-section">
        <div class="h">${esc(sec.heading)}</div>
        <ul>${sec.points.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>
      </div>`
    )
    .join("");
  render(`
    <button class="back" data-action="notes">← Semua nota</button>
    <div class="note-book ${ROUND_COLORS[b.round]}">
      <div class="nb-head">
        <div class="icon" style="margin:0">${ROUND_ICONS[b.round]}</div>
        <div>
          <h3>${esc(b.title)}</h3>
          <div class="scope">${esc(b.scope)}</div>
          <div class="modeline">${esc(b.mode)}</div>
        </div>
        <span class="badge-v ${b.verified ? "ok" : "warn"}" style="margin-left:auto">${
          b.verified ? "✓ Disahkan" : "⚠ Rujuk QB"
        }</span>
      </div>
      ${b.sourceNote ? `<div class="callout warn"><span class="ci">⚠️</span><div>${esc(b.sourceNote)}</div></div>` : ""}
      ${secs}
    </div>
    <div class="runner-actions" style="margin-top:18px">
      <div class="spacer"></div>
      <button class="btn" data-action="round" data-round="${b.round}">Mula Kuiz Round ${b.round} →</button>
    </div>
  `);
}

/* ---------- helpers ---------- */
function esc(str) {
  return String(str == null ? "" : str)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function render(html) {
  const el = app();
  el.innerHTML = `<div class="view">${html}</div>`;
  window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
}

/* ---------- event delegation ---------- */
document.addEventListener("click", (e) => {
  const el = e.target.closest("[data-action]");
  if (!el) return;
  const a = el.dataset.action;
  const round = el.dataset.round;
  switch (a) {
    case "home": setView("home"); break;
    case "quiztab": setView("quiz"); break;
    case "notes": document.querySelector('.tab[data-view="notes"]').classList.add("active"); renderNotes(); break;
    case "round": state.selectedCats = null; renderRoundDetail(round); break;
    case "notebook":
      setActiveTab("notes"); renderNoteBook(round); break;
    case "togglecat": toggleCat(el.dataset.cat, round || currentRound()); break;
    case "start": startSession(round); break;
    case "exitquiz": document.onkeydown = null; renderRoundDetail(round); break;
    case "review": renderReview(round); break;
    case "flip": flipAnswer(el.dataset.idx); break;
  }
});

function setActiveTab(v) {
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.view === v));
}
function currentRound() {
  return state.session?.round;
}
function toggleCat(cat, round) {
  const pool = roundPool(round);
  const sel = state.selectedCats || defaultCats(pool);
  if (sel.has(cat)) { if (sel.size > 1) sel.delete(cat); }
  else sel.add(cat);
  state.selectedCats = sel;
  renderRoundDetail(round);
}
function flipAnswer(idx) {
  const ans = document.getElementById(`ans-${idx}`);
  if (!ans) return;
  const btn = document.querySelector(`[data-action="flip"][data-idx="${idx}"]`);
  const shown = ans.style.display !== "none";
  ans.style.display = shown ? "none" : "block";
  if (btn) btn.textContent = shown ? "Tunjuk jawapan" : "Sembunyi jawapan";
}

document.querySelectorAll(".tab").forEach((t) =>
  t.addEventListener("click", () => setView(t.dataset.view))
);
const homeLink = document.getElementById("homeLink");
homeLink.addEventListener("click", () => setView("home"));
homeLink.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") setView("home"); });

// keyboard activation for cards
document.addEventListener("keydown", (e) => {
  if ((e.key === "Enter" || e.key === " ") && document.activeElement?.dataset?.action) {
    e.preventDefault();
    document.activeElement.click();
  }
});

/* ---------- boot ---------- */
loadData()
  .then(() => setView("home"))
  .catch((err) => {
    app().innerHTML = `<div class="callout warn" style="margin-top:30px"><span class="ci">⚠️</span>
      <div><b>Gagal memuat data.</b><br>${esc(err.message)}<br>
      Jalankan melalui pelayan tempatan: <code>python -m http.server 8765</code> dalam folder app.</div></div>`;
  });
