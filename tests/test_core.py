import fitz
import pytest
from conftest import make_pdf

from pdfloft.core import (
    _parse_pages,
    delete_pages,
    extract_text,
    images_to_pdf,
    info,
    merge,
    pdf_to_images,
    split,
)


class TestMerge:
    def test_merges_page_counts(self, tmp_path, pdf3, pdf2):
        out = merge([pdf3, pdf2], tmp_path / "m.pdf")
        assert info(out)["pages"] == 5

    def test_order_preserved(self, tmp_path, pdf3, pdf2):
        out = merge([pdf3, pdf2], tmp_path / "m.pdf")
        text = extract_text(out)
        assert text.index("hello page 1") < text.index("world page 1")

    def test_single_input_rejected(self, tmp_path, pdf3):
        with pytest.raises(ValueError, match="at least 2"):
            merge([pdf3], tmp_path / "m.pdf")

    def test_creates_parent_dirs(self, tmp_path, pdf3, pdf2):
        out = merge([pdf3, pdf2], tmp_path / "a" / "b" / "m.pdf")
        assert out.exists()

    def test_encrypted_rejected(self, tmp_path, pdf3):
        enc = tmp_path / "enc.pdf"
        enc_val = getattr(fitz, "PDF_ENCRYPT_AES_256", getattr(fitz, "PDF_ENCRYPT_AES256", 2))
        doc = fitz.open(str(pdf3))
        doc.save(str(enc), encryption=enc_val, owner_pw="x", user_pw="x")
        doc.close()
        with pytest.raises(ValueError, match="encrypted"):
            merge([enc, pdf3], tmp_path / "m.pdf")


class TestSplit:
    def test_one_file_per_page(self, tmp_path, pdf3):
        files = split(pdf3, tmp_path / "out")
        assert len(files) == 3
        assert all(f.exists() for f in files)
        assert info(files[1])["pages"] == 1

    def test_naming(self, tmp_path, pdf3):
        files = split(pdf3, tmp_path / "out")
        assert [f.name for f in files] == ["three_p1.pdf", "three_p2.pdf", "three_p3.pdf"]

    def test_split_text_integrity(self, tmp_path, pdf3):
        files = split(pdf3, tmp_path / "out")
        assert "page 2" in extract_text(files[1])


class TestExtractText:
    def test_all_pages(self, pdf3):
        text = extract_text(pdf3)
        assert "page 1" in text and "page 3" in text

    def test_page_spec(self, pdf3):
        text = extract_text(pdf3, pages="2")
        assert "page 2" in text and "page 1" not in text

    def test_range_spec(self, pdf3):
        text = extract_text(pdf3, pages="1-2")
        assert "page 1" in text and "page 3" not in text

    def test_writes_file(self, tmp_path, pdf3):
        out = tmp_path / "out.txt"
        extract_text(pdf3, out_path=out)
        assert "page 2" in out.read_text(encoding="utf-8")


class TestParsePages:
    def test_empty_all(self):
        assert _parse_pages(None, 3) == [0, 1, 2]

    def test_single(self):
        assert _parse_pages("2", 5) == [1]

    def test_range_and_single(self):
        assert _parse_pages("1-2,4", 5) == [0, 1, 3]

    def test_out_of_bounds(self):
        with pytest.raises(ValueError, match="out of bounds"):
            _parse_pages("6", 5)

    def test_reversed_range(self):
        with pytest.raises(ValueError):
            _parse_pages("3-1", 5)


class TestImagesToPdf:
    def test_wraps_pngs(self, tmp_path):
        from PIL import Image

        imgs = []
        for i, color in enumerate(["red", "blue"]):
            p = tmp_path / f"i{i}.png"
            Image.new("RGB", (80, 60), color).save(p)
            imgs.append(p)
        out = images_to_pdf(imgs, tmp_path / "out.pdf")
        assert info(out)["pages"] == 2

    def test_empty_rejected(self, tmp_path):
        with pytest.raises(ValueError, match="no images"):
            images_to_pdf([], tmp_path / "x.pdf")


class TestPdfToImages:
    def test_renders_pngs(self, tmp_path, pdf3):
        files = pdf_to_images(pdf3, tmp_path / "imgs", dpi=72)
        assert len(files) == 3
        assert all(f.stat().st_size > 100 for f in files)

    def test_dpi_scales_size(self, tmp_path, pdf3):
        small = pdf_to_images(pdf3, tmp_path / "s", dpi=72)[0]
        big = pdf_to_images(pdf3, tmp_path / "b", dpi=144)[0]
        assert fitz.Pixmap(str(big)).width > fitz.Pixmap(str(small)).width


class TestInfo:
    def test_fields(self, pdf3, tmp_path):
        d = info(pdf3)
        assert d["pages"] == 3
        assert d["encrypted"] is False
        assert d["file_bytes"] > 0
        assert len(d["page_sizes"]) == 3
        assert d["page_sizes"][0] == (595.0, 842.0)


class TestDeletePages:
    def test_deletes_middle(self, tmp_path, pdf3):
        out = delete_pages(pdf3, "2", tmp_path / "out.pdf")
        assert info(out)["pages"] == 2

    def test_deletes_range(self, tmp_path, pdf3):
        out = delete_pages(pdf3, "1-2", tmp_path / "out.pdf")
        assert info(out)["pages"] == 1
        assert "page 3" in extract_text(out)

    def test_cannot_delete_all(self, tmp_path, pdf3):
        with pytest.raises(ValueError, match="every page"):
            delete_pages(pdf3, "1-3", tmp_path / "out.pdf")


class TestMakePdfHelper:
    def test_roundtrip(self, tmp_path):
        p = make_pdf(tmp_path / "x.pdf", pages=7, text="zzz")
        assert info(p)["pages"] == 7
