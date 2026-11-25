import hashlib
import json
from pathlib import Path

import pymupdf
import pytest

from app.documents.__main__ import main
from app.documents.models import ParsingLimits
from app.documents.parser import PdfParsingError, parse_pdf, parse_pdf_file


def make_pdf(texts: list[str], *, encrypted: bool = False) -> bytes:
    with pymupdf.open() as document:
        for text in texts:
            page = document.new_page()
            if text:
                page.insert_text((72, 72), text)
        if encrypted:
            return bytes(
                document.tobytes(
                    encryption=pymupdf.PDF_ENCRYPT_AES_256,
                    owner_pw="synthetic-owner",
                    user_pw="synthetic-user",
                )
            )
        return bytes(document.tobytes())


def test_text_and_evidence_across_pages() -> None:
    content = make_pdf(["CV fictif\nIngénieur Python", "Projet : API FastAPI"])
    result = parse_pdf(content)
    assert result.page_count == 2
    assert result.document_sha256 == hashlib.sha256(content).hexdigest()
    assert result.warnings == []
    assert "Ingénieur Python" in result.pages[0].text
    assert "FastAPI" not in result.pages[0].text
    assert "Projet : API FastAPI" in result.pages[1].text
    assert result.pages[1].blocks[0].id == "p2-b1"
    x0, y0, x1, y1 = result.pages[0].blocks[0].bbox
    assert x0 == pytest.approx(72)
    assert x0 < x1 and y0 < y1
    assert result.character_count == sum(len(page.text) for page in result.pages)
    assert parse_pdf(content) == result


def test_geometric_order_not_pdf_insertion_order() -> None:
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 200), "Deuxieme bloc")
        page.insert_text((72, 72), "Premier bloc")
        result = parse_pdf(document.tobytes())
    assert result.pages[0].text.index("Premier") < result.pages[0].text.index("Deuxieme")


@pytest.mark.parametrize(
    "texts,warning", [([""], "no_extractable_text"), (["Python", ""], "partial_text")]
)
def test_empty_pages_are_reported(texts: list[str], warning: str) -> None:
    result = parse_pdf(make_pdf(texts))
    assert result.warnings == [warning]
    assert result.pages[-1].warnings == ["no_extractable_text"]


def test_image_only_page_is_not_claimed_as_extracted() -> None:
    with pymupdf.open() as source:
        page = source.new_page()
        page.insert_text((72, 72), "Texte dans une image")
        image = page.get_pixmap().tobytes("png")
    with pymupdf.open() as scanned:
        page = scanned.new_page()
        page.insert_image(page.rect, stream=image)
        result = parse_pdf(scanned.tobytes())
    assert result.pages[0].text == ""
    assert result.warnings == ["no_extractable_text"]


@pytest.mark.parametrize(
    "content,code",
    [(b"", "empty_file"), (b"not pdf", "invalid_pdf"), (b"%PDF-1.7\ninvalid", "invalid_pdf")],
)
def test_invalid_inputs(content: bytes, code: str) -> None:
    with pytest.raises(PdfParsingError) as error:
        parse_pdf(content)
    assert error.value.code == code


def test_encrypted_pdf() -> None:
    with pytest.raises(PdfParsingError) as error:
        parse_pdf(make_pdf(["Secret fictif"], encrypted=True))
    assert error.value.code == "encrypted_pdf"


@pytest.mark.parametrize(
    "limits,code",
    [
        (ParsingLimits(max_bytes=10), "file_too_large"),
        (ParsingLimits(max_pages=1), "too_many_pages"),
        (ParsingLimits(max_characters=3), "too_much_text"),
    ],
)
def test_resource_limits(limits: ParsingLimits, code: str) -> None:
    with pytest.raises(PdfParsingError) as error:
        parse_pdf(make_pdf(["Python", "FastAPI"]), limits)
    assert error.value.code == code


def test_file_and_cli(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "synthetic.pdf"
    source.write_bytes(make_pdf(["Profil fictif Python"]))
    monkeypatch.setattr("sys.argv", ["parser", str(source)])
    assert main() == 0
    output = capsys.readouterr()
    assert "Python" in json.loads(output.out)["pages"][0]["text"]
    assert json.loads(output.err)["duration_ms"] >= 0
    assert "Python" not in output.err
    assert list(tmp_path.iterdir()) == [source]  # Parsing persists no output document.
    with pytest.raises(PdfParsingError) as error:
        parse_pdf_file(source, ParsingLimits(max_bytes=10))
    assert error.value.code == "file_too_large"


def test_cli_error_does_not_expose_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "private-name.pdf"
    monkeypatch.setattr("sys.argv", ["parser", str(source)])
    assert main() == 2
    output = capsys.readouterr()
    assert output.out == ""
    assert json.loads(output.err)["error"] == "file_unreadable"
    assert "private-name" not in output.err
