#!/usr/bin/env python3
"""Zero-dependency deterministic Korean & English prose auditor (Python 3.9+ stdlib)."""

from __future__ import annotations

import argparse
import json
import math
import pathlib
import re
import statistics
import sys
from typing import Any, Dict, List, Optional, Tuple

VALID_GENRES = ("general", "technical", "executive", "essay", "persuasive")

# --- Linguistic & Editorial Pattern Catalog ---

# Linguist-verified true Korean double passives (-이/히/리/기/되 + -어지다).
# Deliberately excludes valid single passives from active roots (만들어지다, 밝혀지다, 지켜지다, 알려지다, 이루어지다, 주어지다, 느껴지다, 나눠지다).
KO_DOUBLE_PASSIVE_RE = re.compile(
    r"(?:보여|쓰여|불려|열려|닫혀|잊혀|믿겨|나뉘어|놓여|풀려|담겨|얽혀|"
    r"되어|잡혀|깎여|쌓여|섞여|꺾여|묶여|덮여|걸려|갈려|읽혀|팔려|찢겨|잘려|밀려|눌려|"
    r"보이어|쓰이어|불리어)"
    r"(?:지[고는면며다자니기]?|졌|진(?=[다\s.,!?)」』\"']|$)|질(?=[지\s.,!?)」』\"']|$)|져)"
)

KO_SLOP_PATTERNS: List[Tuple[str, re.Pattern[str], str]] = [
    ("throat-clearing", re.compile(r"오늘날\s+급변하는"), "Cut throat-clearing opener; start directly with tension or claim."),
    ("throat-clearing", re.compile(r"디지털\s+전환\s+시대에"), "Cut generic era framing; name the exact operational context."),
    ("throat-clearing", re.compile(r"그\s+어느\s+때보다\s+중요"), "Replace generic urgency cliché with concrete stakes or deadline."),
    ("symmetrical-cliche", re.compile(r"단순히\s+[^.!?\n]{2,40}[이가]\s+아니라"), "Avoid mechanical '단순히 A가 아니라 B' contrast; state B directly."),
    ("symmetrical-cliche", re.compile(r"단순한\s+[^.!?\n]{2,30}[을를]\s+넘어"), "Avoid mechanical '단순한 A를 넘어' cliché; state the exact shift."),
    ("empty-authority", re.compile(r"핵심은\s+바로"), "Delete framing filler ('핵심은 바로') and state the claim directly."),
    ("empty-authority", re.compile(r"(?:이|라)고\s+할\s+수\s+있(?:습니다|다)"), "Replace weak hedging wrapper with a direct finite verb."),
    ("buzzword-haze", re.compile(r"혁신적인\s+솔루션"), "Replace vague buzzword with the concrete mechanism or outcome."),
    ("buzzword-haze", re.compile(r"다양한\s+측면에서"), "Replace vague filler with the exact 2-3 dimensions being analyzed."),
    ("buzzword-haze", re.compile(r"패러다임의?\s+전환"), "Replace buzzword with the specific structural before/after change."),
    ("buzzword-haze", re.compile(r"시너지(?:를)?\s+극대화"), "Replace corporate fog with the concrete measurable interaction."),
    ("hollow-wrapup", re.compile(r"지금까지\s+[^.!?\n]{1,40}(?:살펴보았|알아보았)"), "Cut hollow recap closing; end on a decision ask or sharp takeaway."),
    ("hollow-wrapup", re.compile(r"앞으로의?\s+[^.!?\n]{0,20}기대(?:됩니다|된다)"), "Cut empty optimism closing; end with a falsifiable next step or insight."),
]

EN_SLOP_PATTERNS: List[Tuple[str, re.Pattern[str], str]] = [
    ("buzzword-haze", re.compile(r"\bdelve(?:s|d|ing)?\b", re.I), "Replace LLM cliché 'delve' with a concrete verb (examine, inspect, trace)."),
    ("buzzword-haze", re.compile(r"\btapestry\b", re.I), "Replace LLM cliché 'tapestry' with a concrete noun."),
    ("empty-authority", re.compile(r"\btestament\s+to\b", re.I), "Cut 'testament to'; state the causal evidence directly."),
    ("throat-clearing", re.compile(r"\bever-evolving\s+landscape\b", re.I), "Cut throat-clearing cliché; name the concrete change."),
    ("throat-clearing", re.compile(r"\bin\s+today'?s\s+fast-paced\b", re.I), "Delete throat-clearing opener; start with sentence #2."),
    ("empty-authority", re.compile(r"\bit\s+is\s+important\s+to\s+note\b", re.I), "Delete 'it is important to note'; state the fact directly."),
    ("symmetrical-cliche", re.compile(r"\bnot\s+just\s+[^.!?\n]{2,40}\s*(?:—|--|,)\s*(?:it'?s|but)\b", re.I), "Avoid mechanical 'not just X — it's Y' pattern; state Y directly."),
    ("buzzword-haze", re.compile(r"\bgame-?changer\b", re.I), "Replace hype cliché with a measurable delta."),
    ("buzzword-haze", re.compile(r"\bseamlessly\b", re.I), "Replace vague 'seamlessly' with the exact integration behavior."),
    ("hollow-wrapup", re.compile(r"\bin\s+conclusion,\s+as\s+we\s+navigate\b", re.I), "Cut hollow conclusion wrapper."),
]

KO_TRANSLATIONESE_PATTERNS: List[Tuple[str, re.Pattern[str], str]] = [
    ("ko-translationese", re.compile(r"에\s+있어서"), "Replace '~에 있어서' with '~에서', '~할 때', or delete."),
    ("ko-translationese", re.compile(r"에\s+의해(?:서)?"), "Consider active subject instead of passive '~에 의해'."),
    ("ko-translationese", re.compile(r"하는\s+것에\s+대해(?:서)?"), "Simplify '~하는 것에 대해' to direct noun/clause + verb."),
]

KO_JEOK_RE = re.compile(r"[\uAC00-\uD7A3]+적(?:인|으로|이다|입니다)\b")
KO_PLURAL_RE = re.compile(r"[\uAC00-\uD7A3]+들을\b")

KO_NOMINALIZATION_RE = re.compile(
    r"(?:진행하|수행하|실시하|도출하)[고며는다면었겠]|(?:것이|하는\s*게)\s*가능하"
)
EN_NOMINALIZATION_RE = re.compile(
    r"\b(?:make|perform|conduct|carry\s+out|undertake|reach)\s+(?:a|an|the)?\s*\w+(?:tion|sion|ment|ance|ence)\b",
    re.I,
)

KO_UI_PARTICLE_RE = re.compile(r"[\uAC00-\uD7A3]의(?:\s|$)")

KO_HEDGE_RE = re.compile(
    r"(?:아마도|어느\s+정도|일반적으로|다양한|여러\s+가지|상당한|매우|굉장히|어쩌면|비교적)"
)
EN_HEDGE_RE = re.compile(
    r"\b(?:various|somewhat|arguably|significantly|relatively|generally|very|quite|basically|actually)\b",
    re.I,
)

GENERIC_HEADINGS = {
    "서론", "본론", "결론", "개요", "배경", "마무리", "요약", "들어가며", "나가며", "고찰",
    "introduction", "background", "overview", "conclusion", "summary", "discussion",
}

CONCRETE_ANCHOR_RE = re.compile(
    r"(?:\d+(?:\.\d+)?\s*%"
    r"|\d+(?:\.\d+)?\s*(?:ms|sec|min|hr|KB|MB|GB|TB|RPS|QPS|px|s)(?![A-Za-z0-9])"
    r"|\d+(?:\.\d+)?\s*(?:원|만|억|조|배|건|명|개|일|주|개월|년|줄|자|초|분|시간)"
    r"|\b20\d{2}[-./년]\s*\d{1,2}"
    r"|\b\d+(?:,\d{3})+\b"
    r"|`[^`\n]+`"
    r"|\"[^\"\n]{4,60}\")"
)

HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")
LATIN_RE = re.compile(r"[A-Za-z]")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*#*\s*$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.+)$")
BOLD_BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\*\*[^*\n]{1,60}\*\*[:：]?\s*")
TABLE_SEP_RE = re.compile(r"^\s*\|?[\s:-]+\|[\s|:-]*$")
URL_RE = re.compile(r"https?://\S+")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
HTML_COMMENT_SINGLE_RE = re.compile(r"<!--.*?-->")

KO_KNOWN_ENDINGS = (
    "하겠습니다", "되었습니다", "있습니다", "없습니다", "했습니다", "겠습니다",
    "입니다", "됩니다", "합니다", "봅니다", "집니다",
    "겠다", "있다", "없다", "한다", "된다", "이다",
    "해요", "예요", "에요", "어요", "아요", "지요", "군요", "네요",
)


def _hangul_jongseong(ch: str) -> int:
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return (code - 0xAC00) % 28
    return -1


def _preprocess_markdown(text: str) -> Dict[str, Any]:
    """Mask frontmatter, fenced code, blockquotes, HTML comments, and URLs while preserving 1-based line numbers."""
    raw_lines = text.splitlines()
    n = len(raw_lines)
    masked_lines: List[str] = [""] * n
    headings: List[Tuple[int, str]] = []
    bullet_lines = 0
    bold_bullet_lines = 0
    non_empty_prose_lines = 0
    concrete_anchors = 0

    in_frontmatter = False
    in_fence = False
    fence_char = ""
    fence_len = 0
    in_html_comment = False

    for idx, line in enumerate(raw_lines):
        lineno = idx + 1

        # 1. YAML frontmatter at top of document
        if idx == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if line.strip() in {"---", "..."}:
                in_frontmatter = False
            continue

        # 2. Fenced code blocks
        fm = FENCE_RE.match(line)
        if fm:
            marker = fm.group(1)
            if not in_fence:
                in_fence = True
                fence_char = marker[0]
                fence_len = len(marker)
            elif marker[0] == fence_char and len(marker) >= fence_len and line.strip() == marker:
                in_fence = False
            continue
        if in_fence:
            continue

        # 3. HTML comments
        if in_html_comment:
            if "-->" in line:
                in_html_comment = False
                line = line.split("-->", 1)[1]
            else:
                continue
        if "<!--" in line:
            line = HTML_COMMENT_SINGLE_RE.sub("", line)
            if "<!--" in line:
                in_html_comment = True
                line = line.split("<!--", 1)[0]

        stripped = line.strip()
        if not stripped:
            continue

        # 4. Blockquotes & table separator rows & horizontal rules
        if stripped.startswith(">") or TABLE_SEP_RE.match(line) or re.match(r"^\s*([-*_])\1{2,}\s*$", line):
            continue

        # 5. Headings
        hm = HEADING_RE.match(line)
        if hm:
            heading_text = MD_LINK_RE.sub(r"\1", hm.group(2)).strip()
            headings.append((lineno, heading_text))
            masked_lines[idx] = f"__HEADING_BREAK__"
            continue

        # 6. Table data rows (count anchors, exclude from prose sentence stats)
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            concrete_anchors += len(CONCRETE_ANCHOR_RE.findall(stripped))
            masked_lines[idx] = "__SECTION_BREAK__"
            continue

        # Count concrete anchors BEFORE stripping inline code
        concrete_anchors += len(CONCRETE_ANCHOR_RE.findall(line))

        # Track bullet & bold-lead bullet ratios
        if BULLET_RE.match(line):
            bullet_lines += 1
            if BOLD_BULLET_RE.match(line):
                bold_bullet_lines += 1

        # Clean markdown syntax for prose inspection
        cleaned = MD_IMAGE_RE.sub("", line)
        cleaned = MD_LINK_RE.sub(r"\1", cleaned)
        cleaned = URL_RE.sub("", cleaned)
        cleaned = INLINE_CODE_RE.sub(" CODE ", cleaned)
        cleaned = re.sub(r"^\s*(?:[-*+]|\d+\.)\s+", "", cleaned)
        cleaned = re.sub(r"[*_~]+", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        if cleaned:
            masked_lines[idx] = cleaned
            non_empty_prose_lines += 1

    return {
        "masked_lines": masked_lines,
        "headings": headings,
        "bullet_lines": bullet_lines,
        "bold_bullet_lines": bold_bullet_lines,
        "non_empty_prose_lines": non_empty_prose_lines,
        "concrete_anchors": concrete_anchors,
    }


def _detect_language(prose_text: str) -> str:
    hangul = len(HANGUL_RE.findall(prose_text))
    latin = len(LATIN_RE.findall(prose_text))
    total = hangul + latin
    if total == 0:
        return "unknown"
    ratio = hangul / total
    if ratio >= 0.30 and hangul >= 10:
        return "ko"
    if ratio < 0.10:
        return "en"
    return "mixed"


def _split_sentences(masked_lines: List[str]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Group masked lines into paragraphs and sentences while tracking exact 1-based line numbers."""
    paragraphs: List[Dict[str, Any]] = []
    sentences: List[Dict[str, Any]] = []

    cur_lines: List[Tuple[int, str]] = []
    section_id = 0

    def flush_paragraph() -> None:
        if not cur_lines:
            return
        start_line = cur_lines[0][0]
        end_line = cur_lines[-1][0]
        joined = " ".join(txt for _, txt in cur_lines).strip()
        if not joined:
            cur_lines.clear()
            return
        paragraphs.append(
            {
                "startLine": start_line,
                "endLine": end_line,
                "lineCount": len(cur_lines),
                "chars": len(joined),
                "text": joined,
                "sectionId": section_id,
            }
        )

        # Protect decimal numbers and common abbreviations before sentence splitting
        protected = re.sub(r"(\d)\.(\d)", r"\1<DOT>\2", joined)
        protected = re.sub(r"\b(e\.g|i\.e|vs|Dr|Mr|Ms|Prof|Fig|No|Etc)\.", r"\1<DOT>", protected, flags=re.I)
        protected = protected.replace("...", "<ELLIPSIS>")

        parts = re.split(r"(?<=[.!?。])\s+", protected)
        # Approximate line number per sentence by locating substring in cur_lines
        search_idx = 0
        for part in parts:
            sent = part.replace("<DOT>", ".").replace("<ELLIPSIS>", "...").strip()
            if not sent or len(sent) < 3:
                continue
            sent_line = start_line
            probe = sent[:12]
            for i in range(search_idx, len(cur_lines)):
                if probe in cur_lines[i][1]:
                    sent_line = cur_lines[i][0]
                    search_idx = i
                    break
            has_ko = bool(HANGUL_RE.search(sent))
            sentences.append(
                {
                    "line": sent_line,
                    "text": sent,
                    "chars": len(sent),
                    "words": len(re.findall(r"[A-Za-z0-9가-힣'-]+", sent)),
                    "isKo": has_ko,
                    "sectionId": section_id,
                }
            )
        cur_lines.clear()

    for idx, content in enumerate(masked_lines):
        lineno = idx + 1
        if content == "__HEADING_BREAK__":
            flush_paragraph()
            section_id += 1
        elif content == "__SECTION_BREAK__" or not content:
            flush_paragraph()
        else:
            cur_lines.append((lineno, content))
    flush_paragraph()

    return paragraphs, sentences


def _extract_ko_ending(sentence: str) -> Optional[str]:
    trimmed = re.sub(r"[\s.!?。\"'”’)\]」』]+$", "", sentence)
    if not trimmed or not HANGUL_RE.search(trimmed[-1]):
        return None
    # Distinguish specific formal stems (있습니다 / 했습니다 / 합니다 / 입니다 / 됩니다)
    # so varied 하십시오체 sentences do not trigger false monotony alerts.
    for end in KO_KNOWN_ENDINGS:
        if trimmed.endswith(end):
            return end
    # Normalize Korean past-plain endings with 'ㅆ' batchim (jongseong == 20) + '다'
    # e.g., 켰다, 줄었다, 내렸다, 없었다, 받았다, 마쳤다 -> 'ㅆ다'
    if len(trimmed) >= 2 and trimmed[-1] == "다" and _hangul_jongseong(trimmed[-2]) == 20:
        return "ㅆ다"
    if len(trimmed) >= 3 and trimmed.endswith("습니다"):
        return trimmed[-4:] if len(trimmed) >= 4 else trimmed[-3:]
    if len(trimmed) >= 3 and trimmed.endswith("니다") and _hangul_jongseong(trimmed[-3]) == 17:
        return trimmed[-3:]
    if len(trimmed) >= 2 and trimmed[-1] in {"다", "요", "까"}:
        return trimmed[-2:]
    return None


def _excerpt(line_text: str, start: int, end: int, radius: int = 24) -> str:
    lo = max(0, start - radius)
    hi = min(len(line_text), end + radius)
    prefix = "..." if lo > 0 else ""
    suffix = "..." if hi < len(line_text) else ""
    return f"{prefix}{line_text[lo:hi].strip()}{suffix}"


def audit_text(text: str, genre: str = "general", source_name: str = "<stdin>") -> Dict[str, Any]:
    if genre not in VALID_GENRES:
        raise ValueError(f"Unsupported genre '{genre}'. Choose from {', '.join(VALID_GENRES)}.")

    prep = _preprocess_markdown(text)
    masked_lines: List[str] = prep["masked_lines"]
    prose_lines = [(i + 1, ln) for i, ln in enumerate(masked_lines) if ln and ln not in {"__HEADING_BREAK__", "__SECTION_BREAK__"}]
    prose_text = "\n".join(ln for _, ln in prose_lines)
    language = _detect_language(prose_text)
    paragraphs, sentences = _split_sentences(masked_lines)

    char_count = len(prose_text.replace("\n", " ").strip())
    word_count = len(re.findall(r"[A-Za-z0-9가-힣'-]+", prose_text))
    scale_ko = max(char_count / 1000.0, 0.25)
    scale_en = max(word_count / 250.0, 0.25)

    findings: List[Dict[str, Any]] = []

    # 1. Korean Double Passives (P0 error)
    double_passive_hits = 0
    for lineno, ln in prose_lines:
        for m in KO_DOUBLE_PASSIVE_RE.finditer(ln):
            double_passive_hits += 1
            findings.append(
                {
                    "severity": "error",
                    "dimension": "W6",
                    "rule": "ko-double-passive",
                    "line": lineno,
                    "excerpt": _excerpt(ln, m.start(), m.end()),
                    "message": f"Korean double passive '{m.group(0)}' detected (P0 mechanical floor).",
                    "suggestion": "Replace with single passive or active verb (e.g., 보이다, 쓰이다, 불리다, 되다).",
                }
            )

    # 2. Bilingual AI Slop (warning per hit; promoted to P0 error if >= 3 hits or high density)
    slop_matches: List[Dict[str, Any]] = []
    for lineno, ln in prose_lines:
        for rule_sub, pat, hint in KO_SLOP_PATTERNS:
            for m in pat.finditer(ln):
                slop_matches.append(
                    {
                        "line": lineno,
                        "rule": f"ai-slop-{rule_sub}",
                        "match": m.group(0),
                        "excerpt": _excerpt(ln, m.start(), m.end()),
                        "suggestion": hint,
                    }
                )
        for rule_sub, pat, hint in EN_SLOP_PATTERNS:
            for m in pat.finditer(ln):
                slop_matches.append(
                    {
                        "line": lineno,
                        "rule": f"ai-slop-{rule_sub}",
                        "match": m.group(0),
                        "excerpt": _excerpt(ln, m.start(), m.end()),
                        "suggestion": hint,
                    }
                )

    slop_hits = len(slop_matches)
    slop_density = slop_hits / (scale_en if language == "en" else scale_ko)
    slop_is_error = slop_hits >= 3 or (slop_hits >= 2 and slop_density >= 2.0)
    for sm in slop_matches:
        findings.append(
            {
                "severity": "error" if slop_is_error else "warning",
                "dimension": "W7",
                "rule": sm["rule"],
                "line": sm["line"],
                "excerpt": sm["excerpt"],
                "message": f"AI-slop fingerprint '{sm['match']}' detected.",
                "suggestion": sm["suggestion"],
            }
        )

    # 3. Korean Translationese (warning)
    translationese_hits = 0
    jeok_hits = 0
    plural_hits = 0
    for lineno, ln in prose_lines:
        for rule_id, pat, hint in KO_TRANSLATIONESE_PATTERNS:
            for m in pat.finditer(ln):
                translationese_hits += 1
                findings.append(
                    {
                        "severity": "warning",
                        "dimension": "W6",
                        "rule": rule_id,
                        "line": lineno,
                        "excerpt": _excerpt(ln, m.start(), m.end()),
                        "message": f"Korean translationese pattern '{m.group(0)}' detected.",
                        "suggestion": hint,
                    }
                )
        jeok_hits += len(KO_JEOK_RE.findall(ln))
        plural_hits += len(KO_PLURAL_RE.findall(ln))

    if jeok_hits >= 4 and (jeok_hits / scale_ko) > 3.5:
        translationese_hits += jeok_hits
        findings.append(
            {
                "severity": "warning",
                "dimension": "W6",
                "rule": "ko-jeok-overuse",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"{jeok_hits} occurrences ({jeok_hits / scale_ko:.1f} per 1k chars)",
                "message": "Heavy '~적인/~적으로' adjective padding dilutes precision.",
                "suggestion": "Replace vague '~적인' modifiers with specific mechanisms or verbs.",
            }
        )
    if plural_hits >= 3:
        translationese_hits += plural_hits
        findings.append(
            {
                "severity": "warning",
                "dimension": "W6",
                "rule": "ko-plural-calque",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"{plural_hits} occurrences of '~들을'",
                "message": "Repeated English-style plural '~들을' detected.",
                "suggestion": "Drop unnecessary '들' on collective or mass nouns in Korean.",
            }
        )

    # 4. Nominalization & Light-Verb Overuse (warning)
    ko_nom_matches: List[Tuple[int, str, str]] = []
    en_nom_matches: List[Tuple[int, str, str]] = []
    for lineno, ln in prose_lines:
        for m in KO_NOMINALIZATION_RE.finditer(ln):
            ko_nom_matches.append((lineno, m.group(0), _excerpt(ln, m.start(), m.end())))
        for m in EN_NOMINALIZATION_RE.finditer(ln):
            en_nom_matches.append((lineno, m.group(0), _excerpt(ln, m.start(), m.end())))

    nominalization_hits = len(ko_nom_matches) + len(en_nom_matches)
    if len(ko_nom_matches) >= 3 and (len(ko_nom_matches) / scale_ko) >= 2.5:
        for lineno, token, ex in ko_nom_matches[:5]:
            findings.append(
                {
                    "severity": "warning",
                    "dimension": "W6",
                    "rule": "ko-nominalization",
                    "line": lineno,
                    "excerpt": ex,
                    "message": f"Heavy light-verb nominalization '{token}' (total {len(ko_nom_matches)} in doc).",
                    "suggestion": "Use direct action verbs (e.g., 검토를 진행하다 -> 검토하다).",
                }
            )
    for lineno, token, ex in en_nom_matches:
        findings.append(
            {
                "severity": "warning",
                "dimension": "W6",
                "rule": "en-nominalization",
                "line": lineno,
                "excerpt": ex,
                "message": f"Weak verb + nominalization '{token}'.",
                "suggestion": "Convert the noun back into a crisp active verb.",
            }
        )

    # 5. Korean '의' Chaining (3+ per sentence -> warning)
    ui_chain_count = 0
    for sent in sentences:
        if sent["isKo"]:
            hits = len(KO_UI_PARTICLE_RE.findall(sent["text"]))
            if hits >= 3:
                ui_chain_count += 1
                findings.append(
                    {
                        "severity": "warning",
                        "dimension": "W6",
                        "rule": "ko-ui-chaining",
                        "line": sent["line"],
                        "excerpt": sent["text"][:80],
                        "message": f"Possessive particle '의' chained {hits} times in one sentence.",
                        "suggestion": "Break modifier chains into verbs or cleaner noun compounds.",
                    }
                )

    # 6. Korean End-Stop Monotony (3-4 consecutive -> warning, >= 5 -> P0 error)
    ending_monotony_runs = 0
    prev_end: Optional[str] = None
    prev_sec: Optional[int] = None
    run_len = 0
    run_start_line = 1

    def flush_ending_run() -> None:
        nonlocal ending_monotony_runs
        if prev_end and run_len >= 3:
            ending_monotony_runs += 1
            sev = "error" if run_len >= 5 else "warning"
            findings.append(
                {
                    "severity": sev,
                    "dimension": "W6",
                    "rule": "ko-ending-monotony",
                    "line": run_start_line,
                    "excerpt": f"{run_len} consecutive sentences ending in '~{prev_end}'",
                    "message": f"Monotonous Korean sentence ending '~{prev_end}' repeated {run_len} times consecutively.",
                    "suggestion": "Vary sentence structure and verb stems while maintaining consistent register.",
                }
            )

    for sent in sentences:
        end = _extract_ko_ending(sent["text"]) if sent["isKo"] else None
        if end and end == prev_end and sent["sectionId"] == prev_sec:
            run_len += 1
        else:
            flush_ending_run()
            prev_end = end
            prev_sec = sent["sectionId"]
            run_len = 1 if end else 0
            run_start_line = sent["line"]
    flush_ending_run()

    # 7. Sentence Length & Burstiness (CV)
    lengths = [s["words"] if language == "en" else s["chars"] for s in sentences]
    avg_len = round(statistics.mean(lengths), 1) if lengths else 0.0
    median_len = round(statistics.median(lengths), 1) if lengths else 0.0
    stdev_len = round(statistics.pstdev(lengths), 1) if len(lengths) >= 2 else 0.0
    burstiness_cv = round(stdev_len / avg_len, 3) if avg_len > 0 and len(lengths) >= 4 else None

    long_threshold = 35 if language == "en" else 95
    long_unit = "words" if language == "en" else "chars"
    long_sentences = 0
    for sent, slen in zip(sentences, lengths):
        if slen > long_threshold:
            long_sentences += 1
            if long_sentences <= 5:
                findings.append(
                    {
                        "severity": "warning",
                        "dimension": "W6",
                        "rule": "long-sentence",
                        "line": sent["line"],
                        "excerpt": sent["text"][:80],
                        "message": f"Long sentence ({slen} {long_unit} > {long_threshold}).",
                        "suggestion": "Split into two crisp beats or trim nested clauses unless deliberate.",
                    }
                )

    cv_floor = 0.30 if genre == "essay" else 0.22
    if burstiness_cv is not None and len(sentences) >= 6 and burstiness_cv < cv_floor:
        findings.append(
            {
                "severity": "warning",
                "dimension": "W6",
                "rule": "low-burstiness",
                "line": sentences[0]["line"],
                "excerpt": f"CV={burstiness_cv} across {len(sentences)} sentences (floor={cv_floor})",
                "message": f"Monotonic sentence cadence (burstiness CV {burstiness_cv} < {cv_floor}).",
                "suggestion": "Mix longer analytical sentences with short punchy landing sentences.",
            }
        )

    # Detect 5+ consecutive sentences within +/-15% length of each other
    if len(lengths) >= 5:
        for i in range(len(lengths) - 4):
            window = lengths[i : i + 5]
            w_mean = sum(window) / 5.0
            if w_mean > 0 and all(abs(x - w_mean) / w_mean <= 0.15 for x in window):
                findings.append(
                    {
                        "severity": "warning",
                        "dimension": "W6",
                        "rule": "monotonous-cadence-run",
                        "line": sentences[i]["line"],
                        "excerpt": f"Lengths {window} ({long_unit})",
                        "message": "5 consecutive sentences have nearly identical length (+/-15%).",
                        "suggestion": "Break rhythmic monotony with a crisp short sentence or varied clause.",
                    }
                )
                break

    # 8. Structural & Formatting Signals (Bold-lead bullets, Wall of text, Generic headings)
    non_empty = prep["non_empty_prose_lines"]
    bold_bullets = prep["bold_bullet_lines"]
    bold_bullet_ratio = round(bold_bullets / non_empty, 3) if non_empty > 0 else 0.0

    if genre == "essay" and bold_bullets >= 3 and bold_bullet_ratio > 0.20:
        findings.append(
            {
                "severity": "error",
                "dimension": "W7",
                "rule": "essay-bold-bullet-bloat",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"{bold_bullets}/{non_empty} lines ({bold_bullet_ratio * 100:.1f}%)",
                "message": "Bold-lead bullet ratio exceeds 20% in essay mode (P0 AI-slop formatting).",
                "suggestion": "Convert bold-lead bullets into cohesive narrative prose paragraphs.",
            }
        )
    elif genre in {"executive", "general"} and bold_bullets >= 5 and bold_bullet_ratio > 0.50:
        findings.append(
            {
                "severity": "warning",
                "dimension": "W7",
                "rule": "bold-bullet-overuse",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"{bold_bullets}/{non_empty} lines ({bold_bullet_ratio * 100:.1f}%)",
                "message": "Over half of prose lines are bold-lead bullets.",
                "suggestion": "Use connected prose paragraphs for arguments; reserve lists for parallel items.",
            }
        )

    for para in paragraphs:
        if para["chars"] > 380 or para["lineCount"] > 6:
            findings.append(
                {
                    "severity": "warning",
                    "dimension": "W3",
                    "rule": "wall-of-text",
                    "line": para["startLine"],
                    "excerpt": para["text"][:80],
                    "message": f"Dense paragraph ({para['chars']} chars, {para['lineCount']} lines).",
                    "suggestion": "Split at the conceptual turn to improve scan clarity.",
                }
            )

    generic_heading_count = 0
    for lineno, htext in prep["headings"]:
        normalized_h = re.sub(r"^\d+[\.\)]\s*", "", htext).strip().lower()
        if normalized_h in GENERIC_HEADINGS:
            generic_heading_count += 1
            findings.append(
                {
                    "severity": "warning",
                    "dimension": "W3",
                    "rule": "generic-heading",
                    "line": lineno,
                    "excerpt": htext,
                    "message": f"Vague label heading '{htext}' carries no assertion or reader value.",
                    "suggestion": "Rewrite as an assertion heading or concrete functional action.",
                }
            )

    # 9. Hedge / Weasel Words & Concrete Anchors
    hedge_hits = 0
    for _, ln in prose_lines:
        hedge_hits += len(KO_HEDGE_RE.findall(ln)) + len(EN_HEDGE_RE.findall(ln))
    hedge_per_unit = round(hedge_hits / (scale_en if language == "en" else scale_ko), 2)
    hedge_limit = 4.0 if genre in {"technical", "executive"} else 6.0
    if hedge_hits >= 3 and hedge_per_unit >= hedge_limit:
        findings.append(
            {
                "severity": "warning",
                "dimension": "W5",
                "rule": "hedge-weasel-density",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"{hedge_hits} hedges ({hedge_per_unit} per unit, limit {hedge_limit})",
                "message": "High hedge/weasel word density weakens precision and authority.",
                "suggestion": "Replace vague quantifiers ('다양한', '상당한', 'significantly') with bounded specifics.",
            }
        )

    concrete_anchors = prep["concrete_anchors"]
    concrete_per_unit = round(concrete_anchors / (scale_en if language == "en" else scale_ko), 2)
    substantial = (word_count >= 120) if language == "en" else (char_count >= 500)
    if substantial and concrete_anchors == 0:
        findings.append(
            {
                "severity": "warning",
                "dimension": "W5",
                "rule": "low-concreteness",
                "line": prose_lines[0][0] if prose_lines else 1,
                "excerpt": f"0 concrete anchors across {char_count} chars",
                "message": "No verifiable concrete anchors (numbers, units, dates, quotes, or code) found.",
                "suggestion": "Descend Hayakawa's Ladder of Abstraction with real evidence or mark [확인 필요].",
            }
        )

    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]

    return {
        "source": source_name,
        "genre": genre,
        "language": language,
        "ok": len(errors) == 0,
        "errorCount": len(errors),
        "warningCount": len(warnings),
        "stats": {
            "chars": char_count,
            "words": word_count,
            "paragraphs": len(paragraphs),
            "sentences": len(sentences),
            "avgSentenceLen": avg_len,
            "medianSentenceLen": median_len,
            "stdevSentenceLen": stdev_len,
            "burstinessCV": burstiness_cv,
            "boldBulletRatio": bold_bullet_ratio,
            "concreteAnchors": concrete_anchors,
            "concretePerUnit": concrete_per_unit,
            "hedgePerUnit": hedge_per_unit,
        },
        "scores": {
            "doublePassiveHits": double_passive_hits,
            "slopHits": slop_hits,
            "translationeseHits": translationese_hits,
            "nominalizationHits": nominalization_hits,
            "uiChainCount": ui_chain_count,
            "endingMonotonyRuns": ending_monotony_runs,
            "longSentenceCount": long_sentences,
            "genericHeadingCount": generic_heading_count,
        },
        "findings": findings,
    }


def compare_reports(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    b_chars = before["stats"]["chars"]
    a_chars = after["stats"]["chars"]
    char_delta = a_chars - b_chars
    compression_pct = round(((b_chars - a_chars) / b_chars) * 100.0, 1) if b_chars > 0 else 0.0

    b_cv = before["stats"]["burstinessCV"]
    a_cv = after["stats"]["burstinessCV"]
    cv_delta = round(a_cv - b_cv, 3) if (b_cv is not None and a_cv is not None) else None

    delta = {
        "charDelta": char_delta,
        "compressionPct": compression_pct,
        "errorDelta": after["errorCount"] - before["errorCount"],
        "warningDelta": after["warningCount"] - before["warningCount"],
        "doublePassiveDelta": after["scores"]["doublePassiveHits"] - before["scores"]["doublePassiveHits"],
        "slopDelta": after["scores"]["slopHits"] - before["scores"]["slopHits"],
        "translationeseDelta": after["scores"]["translationeseHits"] - before["scores"]["translationeseHits"],
        "endingMonotonyDelta": after["scores"]["endingMonotonyRuns"] - before["scores"]["endingMonotonyRuns"],
        "burstinessCVDelta": cv_delta,
        "concreteAnchorDelta": after["stats"]["concreteAnchors"] - before["stats"]["concreteAnchors"],
    }

    improved = (
        after["ok"]
        and after["errorCount"] <= before["errorCount"]
        and (
            after["errorCount"] < before["errorCount"]
            or after["warningCount"] < before["warningCount"]
            or delta["slopDelta"] < 0
            or delta["translationeseDelta"] < 0
            or compression_pct > 0
        )
    )

    return {
        "mode": "compare",
        "genre": after["genre"],
        "ok": after["ok"],
        "improved": improved,
        "delta": delta,
        "before": {
            "source": before["source"],
            "ok": before["ok"],
            "errorCount": before["errorCount"],
            "warningCount": before["warningCount"],
            "stats": before["stats"],
            "scores": before["scores"],
        },
        "after": after,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Deterministic Korean & English prose auditor (W6/W7/W8).")
    parser.add_argument("target", nargs="?", help="Path to markdown/text file to audit.")
    parser.add_argument("--stdin", action="store_true", help="Read prose from stdin.")
    parser.add_argument("--compare", nargs=2, metavar=("V1", "V2"), help="Compare draft v1 against revised v2.")
    parser.add_argument("--genre", choices=VALID_GENRES, default="general", help="Genre profile for threshold calibration.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on warnings as well as P0 errors.")
    args = parser.parse_args(argv)

    if args.compare:
        p1, p2 = pathlib.Path(args.compare[0]), pathlib.Path(args.compare[1])
        for p in (p1, p2):
            if not p.is_file():
                print(json.dumps({"ok": False, "error": f"File not found: {p}"}, ensure_ascii=False))
                return 2
        rep1 = audit_text(p1.read_text(encoding="utf-8"), genre=args.genre, source_name=str(p1))
        rep2 = audit_text(p2.read_text(encoding="utf-8"), genre=args.genre, source_name=str(p2))
        diff = compare_reports(rep1, rep2)
        print(json.dumps(diff, indent=2, ensure_ascii=False))
        if not diff["ok"]:
            return 1
        if args.strict and rep2["warningCount"] > 0:
            return 1
        return 0

    if args.stdin:
        text = sys.stdin.read()
        source = "<stdin>"
    elif args.target:
        p = pathlib.Path(args.target)
        if not p.is_file():
            print(json.dumps({"ok": False, "error": f"File not found: {p}"}, ensure_ascii=False))
            return 2
        text = p.read_text(encoding="utf-8")
        source = str(p)
    else:
        parser.print_help(sys.stderr)
        return 2

    report = audit_text(text, genre=args.genre, source_name=source)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["ok"]:
        return 1
    if args.strict and report["warningCount"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
