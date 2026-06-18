from dataclasses import dataclass


@dataclass
class ColumnInfo:
    id: str
    name: str
    type: str
    role: str
    examples: list[str]
    description: str
    alias: list[str]
    table_id: str
