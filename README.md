# PdfLoft 📄

**English** | [中文](README_EN.md)

**Every PDF chore in one CLI: merge, split, extract text, images ⇄ PDF, page surgery.** One dependency (PyMuPDF), fully offline.

[![CI](https://github.com/yund229/PdfLoft/actions/workflows/ci.yml/badge.svg)](https://github.com/yund229/PdfLoft/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-1-brightgreen)

![demo](https://cdn.jsdelivr.net/gh/yund229/PdfLoft@main/assets/demo.gif)

## Why

Online PDF tools want you to upload your documents to someone else's server. PdfLoft never touches the network — everything happens on your disk.

## Install

```bash
pip install git+https://github.com/yund229/PdfLoft.git
```

Windows without Python: grab `pdfloft.exe` from [Releases](https://github.com/yund229/PdfLoft/releases).

## Quick start

```bash
pdfloft merge a.pdf b.pdf c.pdf -o combined.pdf    # concatenate in order
pdfloft split report.pdf                           # -> report_p1.pdf, report_p2.pdf, ...
pdfloft text report.pdf -o report.txt --pages 1-3  # selective text extraction
pdfloft img2pdf scan1.png scan2.jpg -o scan.pdf    # images -> one PDF
pdfloft pdf2img slides.pdf --dpi 150               # every page -> PNG
pdfloft info report.pdf                            # JSON: pages, sizes, encryption
pdfloft delete report.pdf --pages 2-4 -o trimmed.pdf
```

## Page specs everywhere

Any command taking `--pages` understands `1`, `1-3`, `1-3,5`, with 1-based numbering and clear out-of-bounds errors.

## Design notes

- **One dependency** — PyMuPDF does parsing, rendering and writing; no pypdf + pdfminer + Pillow pile-up
- **Encrypted PDFs rejected loudly** — a clear `ValueError`, not a cryptic library traceback
- **Real round-trip tested** — the 38 tests generate real PDFs, split them, re-merge them, and assert on the result; no mocks

## Comparison

| | PdfLoft | Online tools | pypdf CLI pile |
|---|---------|--------------|----------------|
| Offline | ✅ | ❌ uploads your files | ✅ |
| Dependencies | 1 | browser | 3-5 |
| Scriptable | ✅ | ❌ | ✅ |
| JSON metadata | ✅ | ❌ | ❌ |

## More tools from me

- [SnapOCR](https://github.com/yund229/SnapOCR) — hotkey screenshot → offline OCR text
- [DirTidy](https://github.com/yund229/DirTidy) — auto-organize your Downloads folder, with undo
- [RectGif](https://github.com/yund229/RectGif) — drag a rectangle on screen, get an animated GIF

## License

MIT
