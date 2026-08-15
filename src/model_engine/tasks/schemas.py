from pydantic import BaseModel, Field


class PaperSummary(BaseModel):
    tldr: str = Field(description="One-paragraph plain-English summary.")
    contributions: list[str] = Field(description="Bullet points, one per contribution.")
    methodology: str = Field(description="How the paper achieves the contributions.")
    limitations: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class MindmapEntity(BaseModel):
    name: str
    type: str = Field(description="e.g. concept, method, dataset, model, task")


class MindmapAndEntities(BaseModel):
    mermaid: str = Field(description="A Mermaid `mindmap` block, ready to paste into Obsidian.")
    entities: list[MindmapEntity] = Field(default_factory=list)


class EmbeddingResult(BaseModel):
    embedding: list[float]
    dimension: int
    model: str


# Schema registry — task config references these by class name.
SCHEMAS: dict[str, type[BaseModel]] = {
    "PaperSummary": PaperSummary,
    "MindmapAndEntities": MindmapAndEntities,
    "EmbeddingResult": EmbeddingResult,
}


def get_schema(name: str | None) -> type[BaseModel] | None:
    if name is None:
        return None
    schema = SCHEMAS.get(name)
    if schema is None:
        raise ValueError(f"Unknown output_schema: {name}. Register it in tasks/schemas.py.")
    return schema
