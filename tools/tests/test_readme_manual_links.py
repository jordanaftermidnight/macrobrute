from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = (ROOT / "README.md").read_text()
RENDERED = ("https://htmlpreview.github.io/?https://github.com/jordanaftermidnight/macrobrute/"
            "blob/main/Macrobrute%20Manual.html")


def test_readme_links_the_raw_manual_and_a_rendered_view():
    assert "(./Macrobrute%20Manual.html)" in README
    assert RENDERED in README
    assert "htmlpreview.github.io is a third-party viewer" in README


def test_manual_file_exists_and_stale_size_is_gone():
    assert (ROOT / "Macrobrute Manual.html").is_file()
    assert "1.7MB" not in README
