"""Usage: python -m app.documents path/to/resume.pdf."""

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import pymupdf

from app.documents.models import ParsingLimits
from app.documents.parser import PdfParsingError, parse_pdf_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraire le texte d'un CV PDF local en JSON.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--max-characters", type=int, default=200_000)
    args = parser.parse_args()
    if min(args.max_bytes, args.max_pages, args.max_characters) <= 0:
        parser.error("Les limites doivent être strictement positives.")
    limits = ParsingLimits(
        max_bytes=args.max_bytes,
        max_pages=args.max_pages,
        max_characters=args.max_characters,
    )
    # Native parser diagnostics can include document details; suppress in this local process.
    pymupdf.TOOLS.mupdf_display_errors(False)
    pymupdf.TOOLS.mupdf_display_warnings(False)
    started = perf_counter()
    try:
        result = parse_pdf_file(args.pdf, limits)
    except PdfParsingError as error:
        print(json.dumps({"error": error.code, "message": str(error)}), file=sys.stderr)
        return 2
    # ASCII escaping keeps JSON portable on Windows terminals with legacy encodings.
    print(json.dumps(result.model_dump(), ensure_ascii=True, indent=2))
    print(json.dumps({"duration_ms": round((perf_counter() - started) * 1000, 3)}), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
