"""
Build the static site so it works BOTH:
  * locally — open  site/index.html  in a browser (file:// works)
  * on GitHub Pages — push the repo and let .github/workflows/deploy.yml publish

Steps:
  1. Run scripts/compute_coverage.py to refresh the % bars on the overview page
  2. Run `mkdocs build`
  3. Copy Credit-Transfer-20260428/ into site/ so PDFs / code / slides linked
     from the pages are reachable via relative paths.
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Force UTF-8 for stdout (Chinese characters in workspace path on Windows)
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SRC_DIR_NAME = "Credit-Transfer-20260428"


def run(cmd: list[str]) -> None:
    print(f"\n$ {' '.join(cmd)}")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    subprocess.run(cmd, check=True, cwd=ROOT, env=env)


def main() -> None:
    run([sys.executable, "scripts/compute_coverage.py"])
    run([sys.executable, "-m", "mkdocs", "build", "--clean"])

    src = ROOT / SRC_DIR_NAME
    dst = SITE / SRC_DIR_NAME
    if not src.exists():
        print(f"WARNING: source folder not found: {src}")
        return
    if dst.exists():
        # Retry once on Windows — Explorer / a file viewer can transiently
        # lock files in site/Credit-Transfer-20260428/.
        try:
            shutil.rmtree(dst)
        except OSError:
            import time
            time.sleep(1.0)
            shutil.rmtree(dst, ignore_errors=True)
            if dst.exists():
                shutil.rmtree(dst)
    print(f"\nCopying source materials  {src}  ->  {dst}")
    # Use the Windows long-path prefix so MAX_PATH (260) doesn't blow up on the
    # deeply-nested PDF / pptx filenames.
    if os.name == "nt":
        src_arg = "\\\\?\\" + str(src.resolve())
        dst_arg = "\\\\?\\" + str(dst.resolve())
    else:
        src_arg, dst_arg = str(src), str(dst)
    shutil.copytree(src_arg, dst_arg)
    n = sum(1 for _ in dst.rglob("*") if _.is_file())
    print(f"Copied {n} files.")

    # Generate index.html for every sub-directory so GitHub Pages can browse them
    _generate_directory_indexes(dst)
    print(f"\n✅ Build complete.  Open:  {SITE / 'index.html'}")


OVERVIEW_URL = "https://zhongshsh.github.io/credit-transfer/"

INDEX_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{folder_name}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #333; }}
    h1 {{ border-bottom: 1px solid #eee; padding-bottom: 10px; font-size: 1.4em; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ padding: 6px 0; }}
    a {{ color: #0366d6; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .back {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
  </style>
</head>
<body>
  <div class="back">
    <a href="../">⬆️ Parent Directory</a>
    <a href="{overview_url}">🏠 Go back to overview</a>
  </div>
  <h1>{folder_name}</h1>
  <ul>
{links}  </ul>
</body>
</html>
"""


def _generate_directory_indexes(root: Path) -> None:
    """Create an index.html in *root* and every sub-directory underneath it."""
    from urllib.parse import quote

    dirs = [root] + sorted(d for d in root.rglob("*") if d.is_dir())
    count = 0
    for d in dirs:
        index_path = d / "index.html"
        if index_path.exists():
            continue
        folder_name = d.name
        items = sorted(d.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        links = ""
        for item in items:
            if item.name == "index.html":
                continue
            encoded = quote(item.name)
            if item.is_dir():
                links += f'    <li>📁 <a href="{encoded}/">{item.name}/</a></li>\n'
            else:
                links += f'    <li>📄 <a href="{encoded}">{item.name}</a></li>\n'
        html = INDEX_TEMPLATE.format(
            folder_name=folder_name,
            overview_url=OVERVIEW_URL,
            links=links,
        )
        index_path.write_text(html, encoding="utf-8")
        count += 1
    print(f"Generated {count} directory index.html files.")


if __name__ == "__main__":
    main()
