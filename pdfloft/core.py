"""Core PDF operations built on PyMuPDF (fitz). All functions are offline."""

from __future__ import annotations

import os
from pathlib import Path

import fitz  # PyMuPDF


def merge(paths: list[str | Path], out_path: str | Path) -> Path:
    """Concatenate PDFs in order into *out_path*."""
    if len(paths) < 2:
        raise ValueError("merge needs at least 2 input PDFs")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for p in paths:
        src = fitz.open(str(p))
        if src.is_encrypted:
            src.close()
            raise ValueError(f"encrypted PDF not supported: {p}")
        doc.insert_pdf(src)
        src.close()
    doc.save(str(out))
    doc.close()
    return out


def split(src: str | Path, out_dir: str | Path) -> list[Path]:
    """Split a PDF into one file per page: name_p1.pdf, name_p2.pdf, ..."""
    doc = fitz.open(str(src))
    if doc.is_encrypted:
        doc.close()
        raise ValueError(f"encrypted PDF not supported: {src}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(src).stem
    written: list[Path] = []
    for i in range(doc.page_count):
        piece = fitz.open()
        piece.insert_pdf(doc, from_page=i, to_page=i)
        target = out_dir / f"{stem}_p{i + 1}.pdf"
        piece.save(str(target))
        piece.close()
        written.append(target)
    doc.close()
    return written


def extract_text(src: str | Path, out_path: str | Path | None = None,
                 pages: str | None = None) -> str:
    """Extract text; optionally restrict to 1-based page spec like '1-3,5'.

    Writes to *out_path* when given (UTF-8) and also returns the text.
    """
    doc = fitz.open(str(src))
    if doc.is_encrypted:
        doc.close()
        raise ValueError(f"encrypted PDF not supported: {src}")
    idx = _parse_pages(pages, doc.page_count)
    chunks = [doc[i].get_text() for i in idx]
    doc.close()
    text = "\n".join(chunks)
    if out_path:
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    return text


def _parse_pages(spec: str | None, count: int) -> list[int]:
    """Turn '1-3,5' into 0-based [0,1,2,4]. Empty spec = all pages."""
    if not spec:
        return list(range(count))
    idx: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a) - 1, int(b) - 1
            if lo < 0 or hi >= count or lo > hi:
                raise ValueError(f"page range out of bounds: {part}")
            idx.extend(range(lo, hi + 1))
        else:
            p = int(part) - 1
            if p < 0 or p >= count:
                raise ValueError(f"page number out of bounds: {part}")
            idx.append(p)
    if not idx:
        raise ValueError("empty page spec")
    return idx


def images_to_pdf(images: list[str | Path], out_path: str | Path,
                  page_size: tuple[float, float] | None = None) -> Path:
    """Wrap images (png/jpg) into a single PDF, one image per page.

    page_size defaults to the image size in points (72 dpi assumption).
    """
    if not images:
        raise ValueError("no images given")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()
    for img in images:
        data = Path(img).read_bytes()
        pix = fitz.Pixmap(data)
        w, h = page_size or (pix.width * 0.75, pix.height * 0.75)  # px->pt @96dpi
        rect = fitz.Rect(0, 0, w, h)
        page = doc.new_page(width=w, height=h)
        page.insert_image(rect, stream=data)
        pix = None
    doc.save(str(out))
    doc.close()
    return out


def pdf_to_images(src: str | Path, out_dir: str | Path, dpi: int = 150) -> list[Path]:
    """Render each page to PNG at *dpi*."""
    doc = fitz.open(str(src))
    if doc.is_encrypted:
        doc.close()
        raise ValueError(f"encrypted PDF not supported: {src}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(src).stem
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    written: list[Path] = []
    for i in range(doc.page_count):
        pix = doc[i].get_pixmap(matrix=mat)
        target = out_dir / f"{stem}_p{i + 1}.png"
        pix.save(str(target))
        written.append(target)
    doc.close()
    return written


def info(src: str | Path) -> dict:
    """Page count, encrypted flag, per-page sizes and file size."""
    doc = fitz.open(str(src))
    try:
        return {
            "pages": doc.page_count,
            "encrypted": bool(doc.is_encrypted),
            "file_bytes": os.path.getsize(src),
            "page_sizes": [(round(p.rect.width, 1), round(p.rect.height, 1)) for p in doc],
        }
    finally:
        doc.close()


def delete_pages(src: str | Path, spec: str, out_path: str | Path) -> Path:
    """Delete pages matching a '1-3,5' spec; write result to *out_path*."""
    doc = fitz.open(str(src))
    if doc.is_encrypted:
        doc.close()
        raise ValueError(f"encrypted PDF not supported: {src}")
    doomed = _parse_pages(spec, doc.page_count)
    if len(doomed) >= doc.page_count:
        doc.close()
        raise ValueError("cannot delete every page")
    for i in sorted(doomed, reverse=True):
        doc.delete_page(i)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    doc.close()
    return out
