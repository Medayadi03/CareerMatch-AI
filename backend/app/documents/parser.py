"""Deterministic text extraction, intentionally independent of HTTP and databases."""

import hashlib
from pathlib import Path
from typing import Literal

import pymupdf

from app.documents.models import ParsedDocument, ParsedPage, ParsingLimits, TextBlock

ErrorCode = Literal[
    "empty_file",
    "file_too_large",
    "invalid_pdf",
    "encrypted_pdf",
    "too_many_pages",
    "too_much_text",
    "file_unreadable",
]


class PdfParsingError(ValueError):
    def __init__(self, code: ErrorCode, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_pdf_file(path: Path, limits: ParsingLimits | None = None) -> ParsedDocument:
    limits = limits or ParsingLimits()
    try:
        # Read at most limit + 1, even if the file grows after it is opened.
        with path.open("rb") as source:
            content = source.read(limits.max_bytes + 1)
    except OSError:
        raise PdfParsingError("file_unreadable", "Impossible de lire le fichier.") from None
    return parse_pdf(content, limits)


def parse_pdf(content: bytes, limits: ParsingLimits | None = None) -> ParsedDocument:
    limits = limits or ParsingLimits()
    if not content:
        raise PdfParsingError("empty_file", "Le fichier est vide.")
    if len(content) > limits.max_bytes:
        raise PdfParsingError("file_too_large", "Le fichier dépasse la taille autorisée.")
    # Strict baseline: reject leading junk rather than trusting a .pdf extension.
    if not content.startswith(b"%PDF-"):
        raise PdfParsingError("invalid_pdf", "Une signature PDF est requise.")

    try:
        with pymupdf.open(stream=content, filetype="pdf") as document:
            if document.needs_pass or document.is_encrypted:
                raise PdfParsingError(
                    "encrypted_pdf", "Les PDF protégés ne sont pas pris en charge."
                )
            if not document.is_pdf or document.page_count < 1:
                raise PdfParsingError("invalid_pdf", "Le document PDF ne contient aucune page.")
            if document.page_count > limits.max_pages:
                raise PdfParsingError(
                    "too_many_pages", "Le PDF dépasse le nombre de pages autorisé."
                )

            result = ParsedDocument(
                parser=f"pymupdf/{pymupdf.VersionBind}",
                document_sha256=hashlib.sha256(content).hexdigest(),
                page_count=document.page_count,
                character_count=0,
                pages=[],
                warnings=["pdf_repaired"] if document.is_repaired else [],
            )
            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                blocks: list[TextBlock] = []
                # No rasterization or OCR; images are not extracted as text blocks.
                for raw in page.get_text("blocks", sort=True, flags=pymupdf.TEXTFLAGS_TEXT):
                    if raw[6] != 0 or not raw[4].strip():
                        continue
                    text = str(raw[4])
                    result.character_count += len(text)
                    if result.character_count > limits.max_characters:
                        raise PdfParsingError(
                            "too_much_text", "Le texte extrait dépasse la limite."
                        )
                    blocks.append(
                        TextBlock(
                            id=f"p{page_index + 1}-b{len(blocks) + 1}",
                            bbox=(float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3])),
                            text=text,
                        )
                    )
                result.pages.append(
                    ParsedPage(
                        number=page_index + 1,
                        width=float(page.cropbox.width),
                        height=float(page.cropbox.height),
                        rotation=page.rotation,
                        text="".join(block.text for block in blocks),
                        blocks=blocks,
                        warnings=[] if blocks else ["no_extractable_text"],
                    )
                )
            empty_pages = sum(not page.blocks for page in result.pages)
            if empty_pages == result.page_count:
                result.warnings.append("no_extractable_text")
            elif empty_pages:
                result.warnings.append("partial_text")
            return result
    except PdfParsingError:
        raise
    except (RuntimeError, ValueError) as error:
        # Never return parser internals or document content in application errors.
        raise PdfParsingError("invalid_pdf", "Le PDF ne peut pas être analysé.") from error
