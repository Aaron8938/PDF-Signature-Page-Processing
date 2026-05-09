#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Signature Page Processing
Scan PDF for pages containing digital signatures,
render signature pages as images and rebuild.
Output saved with "_签章页处理后" suffix next to source.
"""

import argparse
import os
import sys
import tempfile

import fitz  # PyMuPDF
from PIL import Image

VERSION = "v1.0.0"

EMBED_DPI = 200
JPEG_QUALITY = 92

_LANCZOS = getattr(Image, "LANCZOS", getattr(Image, "ANTIALIAS", None))


def sep():
    print("-" * 51)


def find_sig_pages(doc) -> list:
    """Scan open PDF document and return page indices (0-based) containing digital signatures."""
    sig_pages = []
    for i, page in enumerate(doc):
        widgets = page.widgets()
        if widgets:
            for w in widgets:
                if w.field_type_string == "Signature":
                    sig_pages.append(i)
                    break
    return sig_pages


def process_pdf(pdf_path: str) -> str:
    """
    Process PDF: render signature pages as images.
    Returns the output path, or None if no signature pages found.
    """
    doc = fitz.open(pdf_path)
    sig_pages = find_sig_pages(doc)
    total = len(doc)

    if not sig_pages:
        print("  [Info] No signature pages detected. No processing needed.")
        doc.close()
        return None

    print("  Total pages: %d, signature pages: %d" % (total, len(sig_pages)))
    print("  Signature page(s): %s" % [p + 1 for p in sig_pages])

    out_doc = fitz.open()
    mat = fitz.Matrix(EMBED_DPI / 72, EMBED_DPI / 72)
    flatten_set = set(sig_pages)

    for i in range(total):
        page = doc[i]
        if i in flatten_set:
            pix = page.get_pixmap(matrix=mat, alpha=False)
            src_img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            a4_px_w = pix.width
            a4_px_h = pix.height

            tmp_path = None
            try:
                fd, tmp_path = tempfile.mkstemp(suffix=".png")
                os.close(fd)
                src_img.save(tmp_path, "PNG")
                new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(page.rect, filename=tmp_path)
            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass

            print("  [OK] Page %d/%d: signature page -> image" % (i + 1, total))
        else:
            out_doc.insert_pdf(doc, from_page=i, to_page=i)

    out_dir = os.path.dirname(pdf_path)
    base, ext = os.path.splitext(os.path.basename(pdf_path))
    out_name = "%s_签章页处理后%s" % (base, ext)
    out_path = os.path.join(out_dir, out_name)

    out_doc.save(out_path, deflate=True, garbage=4)
    out_doc.close()
    doc.close()

    return out_path


def parse_args():
    parser = argparse.ArgumentParser(description="PDF Signature Page Processing %s" % VERSION)
    parser.add_argument("input_paths", nargs="*", help="PDF file path(s)")
    parser.add_argument("--quality", type=int, default=JPEG_QUALITY,
                        help="JPEG quality for rendered pages (default: %d)" % JPEG_QUALITY)
    return parser.parse_args()


def run_one(pdf_path):
    """Process a single PDF. Returns 0 on success, 1 on skip, 2 on failure."""
    basename = os.path.basename(pdf_path)
    if not pdf_path.lower().endswith('.pdf'):
        print("  [SKIP] %s  (not a PDF)" % basename)
        return 1

    if not os.path.exists(pdf_path):
        print("  [FAIL] %s  (file not found)" % basename)
        return 2

    try:
        output_path = process_pdf(pdf_path)
        if output_path is None:
            return 1
        out_size = os.path.getsize(output_path) / 1024 / 1024
        print("  Output: %s  (%.2f MB)" % (os.path.basename(output_path), out_size))
        return 0
    except Exception as e:
        print("  [FAIL] %s  %s" % (basename, str(e)))
        return 2


def main():
    args = parse_args()

    # CLI paths mode (drag-drop onto BAT)
    if args.input_paths:
        global JPEG_QUALITY
        JPEG_QUALITY = args.quality
        pdfs = [p.strip('"') for p in args.input_paths if p.strip('"').lower().endswith('.pdf')]
        if not pdfs:
            sep()
            print("  No PDF files found")
            sep()
            return 1
        print("  Found %d PDF file(s), processing...\n" % len(pdfs))
        sep()
        ok = skip = fail = 0
        for pdf_path in pdfs:
            result = run_one(pdf_path)
            if result == 0:
                ok += 1
            elif result == 1:
                skip += 1
            else:
                fail += 1
        print()
        sep()
        print("  Done: %d OK  %d skipped  %d failed" % (ok, skip, fail))
        sep()
        return 1 if fail else 0

    # stdin pipe mode
    if not sys.stdin.isatty():
        import io
        paths = []
        for line in io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8").read().splitlines():
            line = line.strip()
            if line:
                paths.extend([p.strip('"') for p in line.split() if p.strip('"').lower().endswith('.pdf')])
        if not paths:
            sep()
            print("  No PDF files found")
            sep()
            return 1
        sep()
        ok = skip = fail = 0
        for pdf_path in paths:
            result = run_one(pdf_path)
            if result == 0:
                ok += 1
            elif result == 1:
                skip += 1
            else:
                fail += 1
        print()
        sep()
        print("  Done: %d OK  %d skipped  %d failed" % (ok, skip, fail))
        sep()
        return 1 if fail else 0

    # Interactive mode — one input, process, then exit
    print()
    print("  Drag a PDF file into this window, or paste path")
    print()

    while True:
        try:
            pdf_path = input("  PDF path: ").strip().strip('"')
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not pdf_path:
            continue
        if not os.path.exists(pdf_path):
            print("  File not found, try again.")
            continue
        if not pdf_path.lower().endswith('.pdf'):
            print("  Not a PDF file, try again.")
            continue
        break

    sep()
    print("  Processing: %s" % os.path.basename(pdf_path))
    print("  Please wait...\n")

    result = run_one(pdf_path)
    print()
    sep()

    if result == 2:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
