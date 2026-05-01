"""
Extract per-page text from each PDF in
    Credit-Transfer-20260428/1-Advanced Algorithms and Programming Techniques/Slices
into scripts/_slices_dump/S<N>.txt for human review.

Each line in the dump is prefixed with `=== p<N> ===` so the auditor can
quickly cite "S3 p.42" when filling in the SYSU page-ref column.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SLICES_DIR = (
    ROOT / "Credit-Transfer-20260428"
    / "1-Advanced Algorithms and Programming Techniques" / "Slices"
)
OUT_DIR = Path(__file__).resolve().parent / "_slices_dump"
OUT_DIR.mkdir(exist_ok=True)


def main() -> None:
    pdfs = sorted(SLICES_DIR.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {SLICES_DIR}")
    for pdf in pdfs:
        m = re.match(r"(\d+)-(.+)\.pdf$", pdf.name)
        if not m:
            continue
        idx, title = m.group(1), m.group(2)
        out = OUT_DIR / f"S{idx}.txt"
        reader = PdfReader(str(pdf))
        with out.open("w", encoding="utf-8") as fh:
            fh.write(f"# S{idx}  {title}\n")
            fh.write(f"# Source: {pdf.name}    Pages: {len(reader.pages)}\n\n")
            for i, page in enumerate(reader.pages, 1):
                try:
                    text = page.extract_text() or ""
                except Exception as exc:
                    text = f"<extract failed: {exc}>"
                # Squash blank lines for readability
                text = re.sub(r"\n{3,}", "\n\n", text.strip())
                fh.write(f"=== p{i} ===\n{text}\n\n")
        print(f"S{idx}: {len(reader.pages):3d} pages -> {out.name}")


if __name__ == "__main__":
    main()
