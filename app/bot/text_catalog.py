from __future__ import annotations

import argparse
from functools import lru_cache
from html import escape
from pathlib import Path
from string import Formatter


TEXTS_DIR = Path(__file__).resolve().parent / "texts"
SOURCE_FILES = ("system.md", "keyboards.md", "public.md", "admin.md", "demo_cases.md")
ALL_TEXTS_FILE = "all.md"


class TextCatalogError(KeyError):
    pass


class _EscapedFormatDict(dict[str, object]):
    def __missing__(self, key: str) -> str:
        raise TextCatalogError(f"Missing text format value: {key}") from None


def _parse_markdown_sections(source: str, file_name: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in source.splitlines():
        if line.startswith("## "):
            current_key = line[3:].strip()
            if not current_key:
                raise TextCatalogError(f"Empty text key in {file_name}")
            if current_key in sections:
                raise TextCatalogError(f"Duplicate text key '{current_key}' in {file_name}")
            sections[current_key] = []
            continue

        if current_key is not None:
            sections[current_key].append(line)

    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


@lru_cache
def load_texts() -> dict[str, str]:
    catalog: dict[str, str] = {}
    for file_name in SOURCE_FILES:
        path = TEXTS_DIR / file_name
        parsed = _parse_markdown_sections(path.read_text(encoding="utf-8"), file_name)
        overlap = catalog.keys() & parsed.keys()
        if overlap:
            joined = ", ".join(sorted(overlap))
            raise TextCatalogError(f"Duplicate text keys across files: {joined}")
        catalog.update(parsed)
    return catalog


def get_raw_text(key: str) -> str:
    try:
        return load_texts()[key]
    except KeyError:
        raise TextCatalogError(f"Unknown text key: {key}") from None


def _format_text(template: str, kwargs: dict[str, object]) -> str:
    Formatter().vformat(template, (), _EscapedFormatDict(kwargs))
    return template.format_map(_EscapedFormatDict(kwargs))


def text(key: str, **kwargs: object) -> str:
    template = get_raw_text(key)
    return _format_text(template, kwargs) if kwargs else template


def html_text(key: str, **kwargs: object) -> str:
    escaped = {name: escape(str(value)) for name, value in kwargs.items()}
    return text(key, **escaped)


def text_lines(key: str) -> list[str]:
    return [line.strip() for line in text(key).splitlines() if line.strip()]


def build_all_markdown() -> str:
    parts: list[str] = ["# All Bot Texts", ""]
    for file_name in SOURCE_FILES:
        path = TEXTS_DIR / file_name
        title = path.stem.replace("_", " ").title()
        parts.extend([f"# {title}", "", path.read_text(encoding="utf-8").strip(), ""])
    return "\n".join(parts).rstrip() + "\n"


def write_all_markdown() -> None:
    (TEXTS_DIR / ALL_TEXTS_FILE).write_text(build_all_markdown(), encoding="utf-8")


def unpack_all_markdown() -> None:
    path = TEXTS_DIR / ALL_TEXTS_FILE
    if not path.exists():
        raise TextCatalogError(f"{ALL_TEXTS_FILE} does not exist to unpack")

    content = path.read_text(encoding="utf-8")

    title_to_file = {}
    for file_name in SOURCE_FILES:
        title = Path(file_name).stem.replace("_", " ").title()
        title_to_file[title] = file_name

    sections: dict[str, list[str]] = {}
    current_file: str | None = None

    for line in content.splitlines():
        if line.startswith("# ") and not line.startswith("## "):
            header = line[2:].strip()
            if header in title_to_file:
                current_file = title_to_file[header]
                sections[current_file] = []
                continue

        if current_file is not None:
            sections[current_file].append(line)

    for file_name, file_lines in sections.items():
        file_content = "\n".join(file_lines).strip() + "\n"
        dest_path = TEXTS_DIR / file_name
        dest_path.write_text(file_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-all", action="store_true")
    parser.add_argument("--unpack", action="store_true")
    args = parser.parse_args()
    if args.write_all:
        write_all_markdown()
    elif args.unpack:
        unpack_all_markdown()


if __name__ == "__main__":
    main()
