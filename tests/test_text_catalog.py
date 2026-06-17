import pytest
from unittest.mock import patch
from app.bot.text_catalog import (
    text,
    html_text,
    text_lines,
    get_raw_text,
    TextCatalogError,
    load_texts,
    build_all_markdown,
    unpack_all_markdown,
    TEXTS_DIR,
    ALL_TEXTS_FILE,
)


@pytest.fixture
def mock_catalog():
    return {
        "test.key": "Hello, {name}!",
        "test.key.no_vars": "Hello, World!",
        "test.key.html": "<b>{name}</b> & {role}",
        "test.key.lines": "  Line 1  \n\n  Line 2  \n",
    }


def test_get_raw_text_success(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        assert get_raw_text("test.key") == "Hello, {name}!"


def test_get_raw_text_not_found(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        with pytest.raises(TextCatalogError) as exc_info:
            get_raw_text("unknown.key")
        assert "Unknown text key: unknown.key" in str(exc_info.value)


def test_text_no_vars(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        assert text("test.key.no_vars") == "Hello, World!"


def test_text_with_vars(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        assert text("test.key", name="Alice") == "Hello, Alice!"


def test_text_missing_vars(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        with pytest.raises(TextCatalogError) as exc_info:
            text("test.key", count=5)
        assert "Missing text format value: name" in str(exc_info.value)


def test_html_text_escapes(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        res = html_text("test.key.html", name="<Alice>", role="&Developer")
        assert res == "<b>&lt;Alice&gt;</b> & &amp;Developer"


def test_text_lines(mock_catalog):
    with patch("app.bot.text_catalog.load_texts", return_value=mock_catalog):
        assert text_lines("test.key.lines") == ["Line 1", "Line 2"]


def test_real_load_texts_not_empty():
    catalog = load_texts()
    assert len(catalog) > 0
    assert "keyboard.home" in catalog


def test_texts_sync():
    aggregate_path = TEXTS_DIR / ALL_TEXTS_FILE
    assert aggregate_path.exists(), f"{ALL_TEXTS_FILE} does not exist!"
    
    current_content = aggregate_path.read_text(encoding="utf-8")
    generated_content = build_all_markdown()
    
    assert current_content.strip() == generated_content.strip(), (
        "Aggregate file all.md is out of sync! "
        "Run `python -m app.bot.text_catalog --write-all` or "
        "`scripts/build_texts_all.ps1` to sync."
    )


def test_unpack_all_markdown_roundtrip(tmp_path):
    mock_texts_dir = tmp_path / "texts"
    mock_texts_dir.mkdir()

    mock_files = {
        "system.md": "# System Texts\n\n## system.test\nValue 1",
        "keyboards.md": "# Keyboard Texts\n\n## keyboard.test\nValue 2",
        "public.md": "# Public Texts\n\n## public.test\nValue 3",
        "admin.md": "# Admin Texts\n\n## admin.test\nValue 4",
        "demo_cases.md": "# Demo Cases Texts\n\n## demo.test\nValue 5",
    }

    for name, content in mock_files.items():
        (mock_texts_dir / name).write_text(content, encoding="utf-8")

    with patch("app.bot.text_catalog.TEXTS_DIR", mock_texts_dir):
        from app.bot.text_catalog import write_all_markdown, unpack_all_markdown
        write_all_markdown()

        all_md_path = mock_texts_dir / "all.md"
        assert all_md_path.exists()

        all_content = all_md_path.read_text(encoding="utf-8")
        modified_content = all_content.replace("Value 1", "Value X")
        all_md_path.write_text(modified_content, encoding="utf-8")

        unpack_all_markdown()

        system_content = (mock_texts_dir / "system.md").read_text(encoding="utf-8")
        assert "Value X" in system_content
        assert "Value 1" not in system_content

        keyboards_content = (mock_texts_dir / "keyboards.md").read_text(encoding="utf-8")
        assert "Value 2" in keyboards_content

