# PdfLoft 📄

[中文](README.md) | **English**

**一个 CLI 搞定所有 PDF 杂活:合并、拆分、提取文本、图片⇄PDF、删页。** 只有一个依赖(PyMuPDF),全程离线。

[![CI](https://github.com/yund229/PdfLoft/actions/workflows/ci.yml/badge.svg)](https://github.com/yund229/PdfLoft/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-1-brightgreen)

![demo](https://cdn.jsdelivr.net/gh/yund229/PdfLoft@main/assets/demo.gif)

## 为什么做这个

在线 PDF 工具要你把文档上传到别人的服务器。PdfLoft 完全不碰网络——一切都在你自己的磁盘上发生。

## 安装

```bash
pip install git+https://github.com/yund229/PdfLoft.git
```

Windows 免装 Python:到 [Releases](https://github.com/yund229/PdfLoft/releases) 下载 `pdfloft.exe`。

## 快速上手

```bash
pdfloft merge a.pdf b.pdf c.pdf -o combined.pdf    # 按顺序合并
pdfloft split report.pdf                           # -> report_p1.pdf, report_p2.pdf, ...
pdfloft text report.pdf -o report.txt --pages 1-3  # 按页提取文本
pdfloft img2pdf scan1.png scan2.jpg -o scan.pdf    # 图片合成 PDF
pdfloft pdf2img slides.pdf --dpi 150               # 每页渲染成 PNG
pdfloft info report.pdf                            # JSON:页数、尺寸、加密状态
pdfloft delete report.pdf --pages 2-4 -o trimmed.pdf
```

## 页码语法

所有接受 `--pages` 的命令都支持 `1`、`1-3`、`1-3,5`,1 起始编号,越界直接报错不吞异常。

## 设计说明

- **只有一个依赖** — PyMuPDF 一件事包揽解析、渲染、写盘,不堆 pypdf + pdfminer + Pillow 三件套
- **加密 PDF 大声拒绝** — 抛出清晰的 `ValueError`,而不是底层库的天书堆栈
- **真实往返测试** — 38 个测试现场生成真 PDF,拆开、再合并、对结果断言;零 mock

## 更多自研小工具

- [SnapOCR](https://github.com/yund229/SnapOCR) — 截图 OCR 取字,离线识别
- [DirTidy](https://github.com/yund229/DirTidy) — 下载文件夹自动整理,可撤销
- [RectGif](https://github.com/yund229/RectGif) — 框选屏幕任意区域直接录 GIF

## License

MIT
