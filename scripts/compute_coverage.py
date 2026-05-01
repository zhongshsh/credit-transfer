"""
Scans docs/request-*/topics.md for coverage badges of the form

    <span class="cov cov-full">Fully Covered</span>
    <span class="cov cov-mostly">Mostly Covered</span>
    <span class="cov cov-partial">Partially Covered</span>
    <span class="cov cov-conceptual">Conceptually Related</span>
    <span class="cov cov-indirect">Indirectly Supported</span>

Scoring model: each row in the topic table = ONE CMU lecture (unit).
A lecture counts as covered to varying degrees:

    Fully      = 1.00   (lecture taught at SYSU)
    Mostly     = 0.75   (main content taught, minor details missing)
    Partial    = 0.50   (about half of the lecture taught)
    Conceptual = 0.25   (only conceptually related, not actually taught)
    Indirect   = 0.00   (only theoretical prerequisites available)

    Coverage = Σ / N_CMU_lectures      Pass threshold = 75 %
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

WEIGHTS = {
    "full":        1.00,
    "mostly":      0.75,
    "partial":     0.50,
    "conceptual":  0.25,
    "indirect":    0.00,
}

BADGE_RE = re.compile(r'<span class="cov cov-([a-z]+)">', re.I)
PASS_THRESHOLD = 0.75


_STRIP_BLOCKS = re.compile(
    r"<!-- COV-INLINE -->.*?<!-- /COV-INLINE -->"
    r"|<!-- LEGEND -->.*?<!-- /LEGEND -->"
    r"|<!-- COV-IGNORE -->.*?<!-- /COV-IGNORE -->",
    re.S,
)


def score_request(topics_md: Path) -> tuple[float, dict[str, int]]:
    text = topics_md.read_text(encoding="utf-8")
    # Remove auto-generated inline coverage block and any explicitly-marked legend
    # so their badges are not double-counted.
    text_clean = _STRIP_BLOCKS.sub("", text)
    # Also drop any line that is clearly a legend (blockquote with "Legend:")
    text_clean = "\n".join(
        ln for ln in text_clean.splitlines()
        if "Legend:" not in ln
    )
    counts: dict[str, int] = {k: 0 for k in WEIGHTS}
    for m in BADGE_RE.finditer(text_clean):
        kind = m.group(1).lower()
        if kind in counts:
            counts[kind] += 1
    total = sum(counts.values())
    if total == 0:
        return 0.0, counts
    score = sum(WEIGHTS[k] * n for k, n in counts.items()) / total
    return score, counts


def render_card(idx: int, score: float, counts: dict[str, int]) -> str:
    pct = f"{score * 100:.2f}"
    pct_width = score * 100
    passed = score >= PASS_THRESHOLD
    bar_cls = "" if passed else "warn"
    score_cls = "cov-pass" if passed else "cov-warn"
    badge = "≥ 75%" if passed else "&lt; 75%"
    total = sum(counts.values())
    breakdown = (
        f'<small>'
        f'🟩 Full {counts["full"]}<br>'
        f'🟩 Mostly {counts["mostly"]}<br>'
        f'🟨 Partial {counts["partial"]}<br>'
        f'⬜ Conceptual {counts["conceptual"]}<br>'
        f'⬛ Indirect {counts["indirect"]}<br>'
        f'(n={total})</small>'
    )
    return (
        f'<div class="cov-bar {bar_cls}"><span style="width:{pct_width}%"></span></div>\n'
        f'<span class="cov-score {score_cls}">Coverage: {pct}% {badge}</span><br>\n'
        f'{breakdown}'
    )


def render_inline(score: float, counts: dict[str, int]) -> str:
    """Compact one-line summary placed at the top of each Lecture-by-lecture mapping."""
    pct = f"{score * 100:.2f}"
    pct_width = score * 100
    passed = score >= PASS_THRESHOLD
    bar_cls = "" if passed else "warn"
    score_cls = "cov-pass" if passed else "cov-warn"
    badge = "≥ 75%" if passed else "&lt; 75%"
    total = sum(counts.values())
    return (
        f'<div class="cov-inline" markdown>\n'
        f'<div class="cov-bar {bar_cls}"><span style="width:{pct_width}%"></span></div>\n'
        f'<span class="cov-score {score_cls}">Coverage: {pct}% {badge}</span> &nbsp;'
        f'<small>'
        f'🟩 Full {counts["full"]} · '
        f'🟩 Mostly {counts["mostly"]} · '
        f'🟨 Partial {counts["partial"]} · '
        f'⬜ Conceptual {counts["conceptual"]} · '
        f'⬛ Indirect {counts["indirect"]} '
        f'(n={total})</small>\n'
        f'</div>'
    )


def main() -> None:
    index_path = DOCS / "index.md"
    index = index_path.read_text(encoding="utf-8")

    summary_lines = []
    for i in range(1, 7):
        topics = DOCS / f"request-{i}" / "topics.md"
        if not topics.exists():
            print(f"[skip] {topics} not found")
            continue
        score, counts = score_request(topics)
        card = render_card(i, score, counts)
        pattern = re.compile(
            rf"<!-- COV:{i} -->.*?<!-- /COV:{i} -->",
            re.S,
        )
        new_block = f"<!-- COV:{i} -->\n{card}\n<!-- /COV:{i} -->"
        if pattern.search(index):
            index = pattern.sub(new_block, index)

        # Also rewrite the inline coverage banner inside each topics.md
        topics_text = topics.read_text(encoding="utf-8")
        inline_pattern = re.compile(
            r"<!-- COV-INLINE -->.*?<!-- /COV-INLINE -->",
            re.S,
        )
        inline_block = (
            f"<!-- COV-INLINE -->\n{render_inline(score, counts)}\n<!-- /COV-INLINE -->"
        )
        if inline_pattern.search(topics_text):
            topics_text = inline_pattern.sub(inline_block, topics_text)
            topics.write_text(topics_text, encoding="utf-8")
        print(f"Request {i}: {score*100:6.2f}%  {counts}")
        summary_lines.append(
            f"| {i} | {score*100:.2f}% | "
            + " · ".join(f"{k}:{v}" for k, v in counts.items() if v)
            + " |"
        )

    index_path.write_text(index, encoding="utf-8")
    print("\nSummary:")
    print("| # | Coverage | Breakdown |")
    print("|---|---|---|")
    for line in summary_lines:
        print(line)


if __name__ == "__main__":
    main()
