"""Shared fixture: generate real multi-page PDFs on the fly (no mocks needed)."""

import fitz
import pytest


def make_pdf(path, pages=3, text="hello"):
    doc = fitz.open()
    for i in range(pages):
        page = doc.new_page(width=595, height=842)  # A4 points
        page.insert_text((72, 100), f"{text} page {i + 1}", fontsize=14)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture
def pdf3(tmp_path):
    return make_pdf(tmp_path / "three.pdf", pages=3)


@pytest.fixture
def pdf2(tmp_path):
    return make_pdf(tmp_path / "two.pdf", pages=2, text="world")
