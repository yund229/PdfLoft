import json

import pytest

from pdfloft.cli import build_parser, main


class TestParser:
    def test_merge_args(self):
        a = build_parser().parse_args(["merge", "a.pdf", "b.pdf", "-o", "m.pdf"])
        assert a.cmd == "merge" and a.inputs == ["a.pdf", "b.pdf"] and a.output == "m.pdf"

    def test_split_default_dir(self):
        a = build_parser().parse_args(["split", "x.pdf"])
        assert a.out_dir is None

    def test_text_pages(self):
        a = build_parser().parse_args(["text", "x.pdf", "--pages", "1-3", "-o", "t.txt"])
        assert a.pages == "1-3" and a.output == "t.txt"

    def test_subcommand_required(self):
        with pytest.raises(SystemExit):
            build_parser().parse_args([])

    def test_version(self, capsys):
        with pytest.raises(SystemExit) as e:
            main(["--version"])
        assert e.value.code == 0
        assert "pdfloft" in capsys.readouterr().out


class TestMainEndToEnd:
    """Run the real CLI against real generated PDFs — no mocks anywhere."""

    def test_merge_flow(self, tmp_path, pdf3, pdf2, capsys):
        out = tmp_path / "m.pdf"
        code = main(["merge", str(pdf3), str(pdf2), "-o", str(out)])
        assert code == 0
        assert out.exists()
        assert "merged" in capsys.readouterr().out

    def test_split_flow(self, tmp_path, pdf3, capsys):
        d = tmp_path / "pages"
        code = main(["split", str(pdf3), "-d", str(d)])
        assert code == 0
        assert len(list(d.glob("*.pdf"))) == 3

    def test_text_to_stdout(self, pdf3, capsys):
        code = main(["text", str(pdf3)])
        out = capsys.readouterr().out
        assert code == 0
        assert "page 2" in out

    def test_text_to_file(self, tmp_path, pdf3, capsys):
        t = tmp_path / "out.txt"
        code = main(["text", str(pdf3), "-o", str(t), "--pages", "1"])
        assert code == 0
        assert "page 1" in t.read_text(encoding="utf-8")
        assert "chars" in capsys.readouterr().out

    def test_info_json(self, pdf3, capsys):
        assert main(["info", str(pdf3)]) == 0
        data = json.loads(capsys.readouterr().out)
        assert data["pages"] == 3

    def test_img2pdf_and_back(self, tmp_path, pdf3, capsys):
        imgs = tmp_path / "imgs"
        main(["pdf2img", str(pdf3), "-d", str(imgs), "--dpi", "72"])
        pngs = sorted(imgs.glob("*.png"))
        assert len(pngs) == 3
        back = tmp_path / "back.pdf"
        main(["img2pdf", *[str(p) for p in pngs], "-o", str(back)])
        assert back.exists()
        assert json.loads(_info(back))["pages"] == 3

    def test_delete_flow(self, tmp_path, pdf3):
        out = tmp_path / "trimmed.pdf"
        code = main(["delete", str(pdf3), "--pages", "1", "-o", str(out)])
        assert code == 0
        assert json.loads(_info(out))["pages"] == 2


def _info(path):
    import io
    from contextlib import redirect_stdout

    from pdfloft.cli import main as m

    buf = io.StringIO()
    with redirect_stdout(buf):
        m(["info", str(path)])
    return buf.getvalue()
