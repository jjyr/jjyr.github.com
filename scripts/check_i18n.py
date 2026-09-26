#!/usr/bin/env python3
"""
Check that all content files in the content/ directory have matching bilingual pairs.
- Chinese page: [name].md
- English page: [name].en.md
"""

from pathlib import Path
import sys

def check_bilingual_pairs(content_dir: Path) -> tuple[list[Path], list[Path]]:
    missing_en: list[Path] = []
    missing_zh: list[Path] = []

    if not content_dir.exists():
        print(f"[ERROR] Content directory not found: {content_dir}", file=sys.stderr)
        return missing_en, missing_zh

    all_files = list(content_dir.rglob("*.md"))

    for file in all_files:
        filename = file.name
        if filename.endswith(".en.md"):
            # English file -> expects Chinese counterpart
            base_name = filename[:-6] + ".md"
            zh_counterpart = file.with_name(base_name)
            if not zh_counterpart.is_file():
                missing_zh.append(zh_counterpart)
        else:
            # Chinese file -> expects English counterpart
            base_name = file.stem + ".en.md"
            en_counterpart = file.with_name(base_name)
            if not en_counterpart.is_file():
                missing_en.append(en_counterpart)

    return sorted(missing_en), sorted(missing_zh)

def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    content_dir = repo_root / "content"

    missing_en, missing_zh = check_bilingual_pairs(content_dir)

    if missing_en or missing_zh:
        print("\n" + "=" * 65, file=sys.stderr)
        print("[WARNING] Git commit blocked: Incomplete bilingual content!", file=sys.stderr)
        print("=" * 65, file=sys.stderr)

        if missing_en:
            print("\nMissing English translation (.en.md):", file=sys.stderr)
            for path in missing_en:
                zh_src = path.with_name(path.name[:-6] + ".md")
                rel_en = path.relative_to(repo_root)
                rel_zh = zh_src.relative_to(repo_root)
                print(f"  - {rel_en}  (source: {rel_zh})", file=sys.stderr)

        if missing_zh:
            print("\nMissing Chinese translation (.md):", file=sys.stderr)
            for path in missing_zh:
                en_src = path.with_name(path.stem + ".en.md")
                rel_zh = path.relative_to(repo_root)
                rel_en = en_src.relative_to(repo_root)
                print(f"  - {rel_zh}  (source: {rel_en})", file=sys.stderr)

        print("\nPlease translate missing pages or run:", file=sys.stderr)
        print("  uv run python scripts/translate.py --missing\n", file=sys.stderr)
        print("=" * 65 + "\n", file=sys.stderr)
        return 1

    print("[i18n check] All bilingual content pages are complete and paired.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
