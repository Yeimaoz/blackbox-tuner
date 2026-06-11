import tarfile
import zipfile
from pathlib import Path

import pytest


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
        "5965696d616f7a",   # username / home-dir path leak guard
    ]
]


def test_public_tree_has_no_private_terms():
    """Scan working tree for private terms.

    Known Limitation: git history is not scanned.  If a private term was
    committed and later removed, the term still exists in old commits and is
    visible to anyone who clones the repo.  This test only covers the current
    working tree.
    """
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
            if _contains_term(text, term):
                offenders.append(f"{path.relative_to(root)} contains forbidden term")
    assert offenders == []


def test_release_archives_have_no_private_terms():
    root = Path(__file__).resolve().parents[1]
    artifacts = list(root.glob("dist/*"))
    if not artifacts:
        pytest.skip("dist/ has no build artifacts; run 'python -m build' first")
    offenders = []
    for path in artifacts:
        if path.suffix == ".whl":
            offenders.extend(_scan_zip(path))
        elif path.suffixes[-2:] == [".tar", ".gz"]:
            offenders.extend(_scan_tar(path))
    assert offenders == []


def _scan_zip(path):
    offenders = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            _scan_name(path, name, offenders)
            if _is_text_name(name):
                text = archive.read(name).decode("utf-8", errors="ignore").lower()
                _scan_text(path, name, text, offenders)
    return offenders


def _scan_tar(path):
    offenders = []
    with tarfile.open(path, "r:gz") as archive:
        for member in archive.getmembers():
            _scan_name(path, member.name, offenders)
            if member.isfile() and _is_text_name(member.name):
                handle = archive.extractfile(member)
                if handle is None:
                    continue
                text = handle.read().decode("utf-8", errors="ignore").lower()
                _scan_text(path, member.name, text, offenders)
    return offenders


def _scan_name(archive_path, name, offenders):
    for term in FORBIDDEN_TERMS:
        if _contains_term(name, term):
            offenders.append(f"{archive_path.name}:{name} contains forbidden term")


def _scan_text(archive_path, name, text, offenders):
    for term in FORBIDDEN_TERMS:
        if _contains_term(text, term):
            offenders.append(f"{archive_path.name}:{name} contains forbidden term")


def _is_text_name(name):
    return name.endswith((".py", ".md", ".toml", ".txt", "METADATA", "PKG-INFO", "WHEEL", "RECORD"))


def _contains_term(text, term):
    if term == bytes.fromhex("534944").decode("utf-8"):
        return term in text
    return term.lower() in text.lower()
