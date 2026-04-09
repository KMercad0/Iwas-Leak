# BUCM ATLAS - PDF Watermark Tool

A desktop tool that batch-watermarks PDFs with names from a CSV file. Built for Bicol University College of Medicine's ATLAS (Teaching and Learning Academic Society) to mark distributed documents per recipient.

## Features

- **Batch watermarking** — reads names from the 3rd column of a CSV and generates one watermarked PDF per name
- **Works with multi-page documents and mixed page sizes**
- **Adjustable opacity** — slider control from 5% to 50%
- **Adjustable density** — control watermark coverage from a single centered mark to a full-page grid (1–5)
- **Progress tracking** — real-time status and progress bar during processing
- **Ready indicator** — button turns green when all inputs are selected
- **Clean UI** — centered layout with the BUCM seal, green color scheme

## Requirements

- Python 3.8+

Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies: `PyMuPDF`, `pandas`, `Pillow` (tkinter included with Python)

## Usage

```bash
python main.py
```

1. **Select PDF** — the document to watermark
2. **Select CSV** — must have at least 3 columns; names are read from the 3rd column
3. **Select Output Folder** — where watermarked PDFs will be saved
4. Adjust **Opacity** and **Density** sliders as needed
5. Click **Watermark PDF** (turns green when ready)

Output files are named `originalname_RecipientName.pdf` (spaces replaced with underscores).

## Packaging as EXE

```bash
pip install pyinstaller
pyinstaller main.spec
```

The EXE will be in the `dist/` folder as `BUCM_ATLAS.exe`.

## Tech Stack

| Component | Library |
|---|---|
| PDF engine | [PyMuPDF](https://pymupdf.readthedocs.io/) (fitz) |
| CSV parsing | pandas |
| UI | tkinter |
| Background image | Pillow |

## Credits

Envisioned by **11th Regulus Internus Orange Gandia** | Made by **KMercad0**
