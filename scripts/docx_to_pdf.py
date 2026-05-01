"""
Convert every .docx under Credit-Transfer-20260428/ to a same-name .pdf
(in the same folder), using Microsoft Word COM automation.

Skips files whose .pdf already exists. Skips anything under site/ (build output).

Usage:  python scripts/docx_to_pdf.py
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "Credit-Transfer-20260428"
WD_FORMAT_PDF = 17  # Word constant for "save as PDF"


def main() -> None:
    try:
        import win32com.client  # type: ignore
    except ImportError:
        print("ERROR: pywin32 not installed.  Run:  python -m pip install pywin32 --user")
        sys.exit(1)

    docx_files = [
        p for p in SOURCE.rglob("*.docx")
        if not p.name.startswith("~$")  # skip Word lock files
    ]
    print(f"Found {len(docx_files)} .docx files under {SOURCE}")

    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0  # wdAlertsNone

    converted = skipped = failed = 0
    try:
        for src in docx_files:
            dst = src.with_suffix(".pdf")
            if dst.exists():
                print(f"[skip] {src.relative_to(ROOT)}  (PDF already exists)")
                skipped += 1
                continue
            print(f"[conv] {src.relative_to(ROOT)}")
            doc = None
            try:
                src_arg = str(src.resolve())
                dst_arg = str(dst.resolve())
                doc = word.Documents.Open(src_arg, ReadOnly=True)
                doc.SaveAs(dst_arg, FileFormat=WD_FORMAT_PDF)
                converted += 1
            except Exception as e:
                print(f"   FAILED: {e}")
                failed += 1
            finally:
                if doc is not None:
                    doc.Close(SaveChanges=False)
    finally:
        word.Quit()

    print(f"\nDone. converted={converted}  skipped={skipped}  failed={failed}")


if __name__ == "__main__":
    main()
