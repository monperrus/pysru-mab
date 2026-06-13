from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import TypedDict


class CodeInfo(TypedDict):
    label: str
    description: str
    field_type: str


def _normalize_codes(codes: dict[str, dict[str, str]]) -> dict[str, CodeInfo]:
    return {
        code: CodeInfo(
            label=info["label"],
            description=info.get("description", ""),
            field_type=info.get("field_type", "amount"),
        )
        for code, info in codes.items()
    }


@lru_cache
def _load_builtin_tables() -> dict[str, dict[str, CodeInfo]]:
    tables: dict[str, dict[str, CodeInfo]] = {}
    data_dir = resources.files("pysru_mab") / "data"
    for entry in data_dir.iterdir():
        if entry.name.endswith(".json"):
            data = json.loads(entry.read_text(encoding="utf-8"))
            tables[data["form"].upper()] = _normalize_codes(data["codes"])
    return tables


def codes_for_form(form_name: str) -> dict[str, CodeInfo] | None:
    return _load_builtin_tables().get(form_name.upper())


def describe(form_name: str, code: str) -> CodeInfo | None:
    table = codes_for_form(form_name)
    if table is None:
        return None
    return table.get(code)


def available_forms() -> list[str]:
    return sorted(_load_builtin_tables().keys())


def load_custom_table(path: str) -> dict[str, dict[str, CodeInfo]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {data["form"].upper(): _normalize_codes(data["codes"])}
