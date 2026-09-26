#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pyyaml>=6.0",
# ]
# ///
"""
Translate Chinese Markdown content files into English (.en.md) using the agy CLI.
Only translates titles and textual body content.
Preserves YAML metadata (dates, drafts, build flags), code blocks, inline code, and URLs.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
import yaml


def find_agy_binary(custom_path: str | None = None) -> str:
    if custom_path and os.path.exists(custom_path):
        return custom_path

    which_agy = shutil.which("agy")
    if which_agy:
        return which_agy

    for candidate in ["/opt/homebrew/bin/agy", "/usr/local/bin/agy"]:
        if os.path.exists(candidate):
            return candidate

    raise RuntimeError("agy binary not found. Please ensure agy CLI is installed and in PATH.")


def call_agy(prompt: str, agy_path: str, model: str | None = None) -> str:
    cmd = [agy_path, "--disable-slash-commands", "-p", prompt]
    if model:
        cmd.extend(["--model", model])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"agy CLI failed with code {res.returncode}:\n{res.stderr}\n{res.stdout}")

    return res.stdout.strip()


def strip_markdown_fence(text: str) -> str:
    text = text.strip()
    # If the LLM wrapped the entire response in ```markdown ... ``` or ``` ... ```
    if text.startswith("```"):
        first_line_end = text.find("\n")
        if first_line_end != -1 and text.endswith("```"):
            inner = text[first_line_end + 1 : -3].strip()
            return inner
    return text


def split_frontmatter(content: str) -> tuple[str, dict, str]:
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_fm = f"---{parts[1]}---"
            yaml_str = parts[1].strip()
            parsed_fm = yaml.safe_load(yaml_str) or {}
            body = parts[2].lstrip("\r\n")
            return raw_fm, parsed_fm, body
    return "", {}, content


def replace_title_in_frontmatter(frontmatter: str, new_title: str) -> str:
    escaped_title = new_title.replace('"', '\\"')
    pattern = r'^(title\s*:\s*)(["\'].*?["\']|.*?)$'
    subst = f'\\g<1>"{escaped_title}"'
    return re.sub(pattern, subst, frontmatter, flags=re.MULTILINE)


def translate_title(title: str, agy_path: str, model: str | None = None) -> str:
    prompt = (
        "Translate the following blog post title from Chinese to English.\n"
        "Output ONLY the translated title text. Do not include quotes, markdown formatting, or explanations.\n\n"
        f"Title: {title}"
    )
    translated = call_agy(prompt, agy_path, model)
    # Strip any extra quotes or backticks
    translated = translated.strip('"`\' \n\r')
    return translated


def translate_body(body: str, agy_path: str, model: str | None = None) -> str:
    if not body.strip():
        return ""

    prompt = (
        "You are a professional technical translator and writer.\n"
        "Translate the following Markdown content from Chinese to English.\n\n"
        "CRITICAL RULES:\n"
        "1. Translate all Chinese prose, headings, and explanations accurately and idiomatically into English.\n"
        "2. DO NOT translate code blocks (```...```) or inline code (`...`). Keep code and commands completely untouched.\n"
        "3. For Markdown links [text](url), translate the link text, but DO NOT modify the URL.\n"
        "4. DO NOT translate HTML tags, image paths, or markdown formatting.\n"
        "5. Output ONLY the translated Markdown. Do not include any greeting, preamble, commentary, or outer markdown wrapper around the entire document.\n\n"
        "Content:\n"
        f"{body}"
    )
    raw_res = call_agy(prompt, agy_path, model)
    return strip_markdown_fence(raw_res)


def translate_file(file_path: Path, agy_path: str, model: str | None = None, force: bool = False) -> Path | None:
    if file_path.name.endswith(".en.md"):
        print(f"[SKIP] Already an English file: {file_path}")
        return None

    target_name = file_path.stem + ".en.md"
    target_path = file_path.with_name(target_name)

    if target_path.exists() and not force:
        print(f"[SKIP] Target already exists: {target_path} (use --force to overwrite)")
        return target_path

    print(f"Translating {file_path} -> {target_path} ...")
    content = file_path.read_text(encoding="utf-8")
    raw_fm, parsed_fm, body = split_frontmatter(content)

    new_fm = raw_fm
    if "title" in parsed_fm:
        original_title = str(parsed_fm["title"])
        print(f"  Translating title: '{original_title}'")
        en_title = translate_title(original_title, agy_path, model)
        print(f"  -> '{en_title}'")
        new_fm = replace_title_in_frontmatter(raw_fm, en_title)

    if body.strip():
        print(f"  Translating Markdown body ({len(body)} characters)...")
        en_body = translate_body(body, agy_path, model)
    else:
        en_body = ""

    if new_fm:
        output_content = f"{new_fm}\n\n{en_body}".strip() + "\n"
    else:
        output_content = en_body.strip() + "\n"

    target_path.write_text(output_content, encoding="utf-8")
    print(f"[DONE] Written to {target_path}\n")
    return target_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate blog Markdown pages to English using agy CLI")
    parser.add_argument("files", nargs="*", help="Specific .md files to translate")
    parser.add_argument("--missing", action="store_true", help="Automatically find and translate all missing .en.md files")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing .en.md files")
    parser.add_argument("--model", help="Specify AI model to use with agy CLI")
    parser.add_argument("--agy-path", help="Path to agy binary")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    content_dir = repo_root / "content"

    try:
        agy_path = find_agy_binary(args.agy_path)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    targets: list[Path] = []

    if args.files:
        for f in args.files:
            p = Path(f)
            if not p.is_absolute():
                p = (repo_root / p).resolve()
            if not p.is_file():
                print(f"[ERROR] File not found: {p}", file=sys.stderr)
                return 1
            targets.append(p)
    elif args.missing:
        for md_file in content_dir.rglob("*.md"):
            if not md_file.name.endswith(".en.md"):
                en_file = md_file.with_name(md_file.stem + ".en.md")
                if not en_file.exists():
                    targets.append(md_file)
        if not targets:
            print("[INFO] No missing translations found! All pages have .en.md counterparts.")
            return 0
    else:
        parser.print_help()
        return 0

    print(f"Found {len(targets)} file(s) to translate using agy ({agy_path}).\n")

    for file_path in targets:
        try:
            translate_file(file_path, agy_path, model=args.model, force=args.force)
        except Exception as e:
            print(f"[ERROR] Failed to translate {file_path}: {e}", file=sys.stderr)
            return 1

    print("[SUCCESS] All requested files translated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
