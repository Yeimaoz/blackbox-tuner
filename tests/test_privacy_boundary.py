from pathlib import Path


FORBIDDEN_TERMS = [
    bytes.fromhex(value).decode("utf-8")
    for value in [
        "6c637a",
        "73656e74696e656c",
        "534944",
        "5368696f616a69",
        "42696e616e6365",
        "536861727065",
        "4b656c6c79",
        "736861646f77",
        "706970656c696e655f737461747573",
        "63727970746f",
        "66757475726573",
        "6f7074696f6e73",
        "74726164696e67",
        "7374726174656779",
        "62726f6b6572",
        "65786368616e6765",
        "446973636f7264",
        "776562686f6f6b",
        "6d61696c626f78",
    ]
]


def test_public_tree_has_no_private_terms():
    root = Path(__file__).resolve().parents[1]
    checked_suffixes = {".py", ".md", ".toml"}
    ignored_parts = {".git", ".venv", ".pytest_cache", "build", "dist"}
    offenders = []
    for path in root.rglob("*"):
        if ignored_parts.intersection(path.parts) or path.suffix not in checked_suffixes:
            continue
        if any(part.endswith(".egg-info") for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in text:
                offenders.append(f"{path.relative_to(root)} contains forbidden term")
    assert offenders == []
