"""Command-line interface for PdfLoft."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, core


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pdfloft",
        description="Every PDF chore in one CLI: merge, split, text, convert.",
    )
    p.add_argument("--version", action="version", version=f"pdfloft {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("merge", help="concatenate PDFs in order")
    sp.add_argument("inputs", nargs="+", help="2+ input PDFs")
    sp.add_argument("-o", "--output", required=True)

    sp = sub.add_parser("split", help="one PDF per page")
    sp.add_argument("input")
    sp.add_argument("-d", "--out-dir", default=None)

    sp = sub.add_parser("text", help="extract text")
    sp.add_argument("input")
    sp.add_argument("-o", "--output", default=None, help="write text to file")
    sp.add_argument("--pages", default=None, help="e.g. 1-3,5")

    sp = sub.add_parser("img2pdf", help="wrap images into a PDF")
    sp.add_argument("inputs", nargs="+", help="png/jpg images")
    sp.add_argument("-o", "--output", required=True)

    sp = sub.add_parser("pdf2img", help="render pages to PNG")
    sp.add_argument("input")
    sp.add_argument("-d", "--out-dir", default=None)
    sp.add_argument("--dpi", type=int, default=150)

    sp = sub.add_parser("info", help="page count and sizes, as JSON")
    sp.add_argument("input")

    sp = sub.add_parser("delete", help="delete pages, e.g. --pages 1-3,5")
    sp.add_argument("input")
    sp.add_argument("--pages", required=True)
    sp.add_argument("-o", "--output", required=True)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    c = args.cmd

    if c == "merge":
        out = core.merge(args.inputs, args.output)
        print(f"merged {len(args.inputs)} PDFs -> {out}")
    elif c == "split":
        out_dir = args.out_dir or str(args.input) + "_pages"
        files = core.split(args.input, out_dir)
        print(f"split into {len(files)} files in {out_dir}")
    elif c == "text":
        text = core.extract_text(args.input, args.output, args.pages)
        if args.output:
            print(f"text -> {args.output} ({len(text)} chars)")
        else:
            sys.stdout.write(text)
    elif c == "img2pdf":
        out = core.images_to_pdf(args.inputs, args.output)
        print(f"{len(args.inputs)} images -> {out}")
    elif c == "pdf2img":
        out_dir = args.out_dir or str(args.input) + "_images"
        files = core.pdf_to_images(args.input, out_dir, args.dpi)
        print(f"rendered {len(files)} PNGs in {out_dir}")
    elif c == "info":
        print(json.dumps(core.info(args.input), ensure_ascii=False))
    elif c == "delete":
        out = core.delete_pages(args.input, args.pages, args.output)
        print(f"kept pages -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
