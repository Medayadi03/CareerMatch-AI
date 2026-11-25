from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ParsingLimits(BaseModel):
    model_config = ConfigDict(frozen=True)

    max_bytes: int = Field(default=10 * 1024 * 1024, gt=0)
    max_pages: int = Field(default=20, gt=0)
    max_characters: int = Field(default=200_000, gt=0)


class TextBlock(BaseModel):
    id: str
    bbox: tuple[float, float, float, float]
    text: str


class ParsedPage(BaseModel):
    number: int = Field(ge=1)
    width: float
    height: float
    rotation: int
    text: str
    blocks: list[TextBlock]
    warnings: list[Literal["no_extractable_text"]]


class ParsedDocument(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    parser: str
    document_sha256: str
    page_count: int
    character_count: int
    pages: list[ParsedPage]
    warnings: list[Literal["pdf_repaired", "no_extractable_text", "partial_text"]]
