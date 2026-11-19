# Writing Kit Editorial Invariants

These always-on rules remain concise (< 2 KB) and apply across Claude Code, Codex CLI, and Antigravity CLI whenever Writing Kit is active.

## 1. Epistemic Honesty (Zero Fabrication)
- Never invent statistics, benchmark numbers, citations, survey percentages, or quotes to make prose sound persuasive.
- When supporting evidence is missing, insert an explicit `[확인 필요: 구체 지표/근거]` placeholder instead of guessing.

## 2. Author Ownership Over Generic Ghostwriting
- Do not overwrite the author's original judgment with hollow boilerplate.
- When core inputs (audience/shift, falsifiable thesis, authentic evidence) are missing in substantial writing tasks, elicit only the missing pieces (max 3 questions) or declare explicit assumptions up front.

## 3. Anti-Slop & Mechanical Floor
- Eliminate throat-clearing openings (`오늘날 급변하는...`, `In today's fast-paced world...`), mechanical symmetrical clichés (`단순히 A가 아니라 B`, `not just X, it's Y`), Korean double passives (`보여지다`, `쓰여지다`, `되어지다`), and hollow wrap-up endings (`앞으로가 기대됩니다`).
- Run `prose_audit.py` on substantial drafts and revisions (>= 300 chars) before claiming prose is polished.

## 4. Context Economics (Progressive Disclosure)
- Load only the single matching genre profile from `skills/world-class-writing/references/` on demand; never bulk-load all genre references into context at once.
