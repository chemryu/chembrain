import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MoleculeInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    smiles: str = Field(min_length=1, max_length=2000)
    aliases: list[str] = Field(default_factory=list, max_length=30)
    availability: Literal["in_stock", "order", "unknown"] = "unknown"
    notes: str = Field(default="", max_length=10000)

    @field_validator("name", "smiles")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("빈 값은 사용할 수 없습니다.")
        return value.strip()


class Evidence(BaseModel):
    source_id: str
    page: int = Field(ge=1)
    quote: str = Field(min_length=1, max_length=10000)
    locator: str = Field(default="", max_length=300)


class SourceMetadataInput(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    doi: str = Field(default="", max_length=200)
    citation: str = Field(default="", max_length=2000)
    document_role: Literal["main", "supplement", "notes", "other"] = "other"
    related_source_ids: list[str] = Field(default_factory=list, max_length=20)
    notes: str = Field(default="", max_length=10000)

    @field_validator("title")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("자료 제목을 입력하세요.")
        return value.strip()

    @field_validator("doi")
    @classmethod
    def doi_format(cls, value: str) -> str:
        value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I)
        if value and not re.fullmatch(r"10\.\d{4,9}/[^\s]+", value):
            raise ValueError("DOI 형식을 확인하세요. 예: 10.1126/science.1255525")
        return value


class ReactionInput(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: Literal["organic", "electrochemical", "photochemical"] = "organic"
    reactants: list[str] = Field(min_length=1, max_length=30)
    products: list[str] = Field(min_length=1, max_length=30)
    reagents: str = Field(default="", max_length=2000)
    conditions: dict[str, str] = Field(default_factory=dict)
    yield_percent: float | None = Field(default=None, ge=0, le=100)
    status: Literal["draft", "reviewed"] = "draft"
    evidence: list[Evidence] = Field(default_factory=list, max_length=30)
    notes: str = Field(default="", max_length=10000)

    @field_validator("name")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("반응 이름을 입력하세요.")
        return value.strip()

    @field_validator("conditions")
    @classmethod
    def bounded_conditions(cls, value: dict[str, str]) -> dict[str, str]:
        if len(value) > 40 or any(len(k) > 100 or len(v) > 2000 for k, v in value.items()):
            raise ValueError("조건 필드가 너무 큽니다.")
        return value
