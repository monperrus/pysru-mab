from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

_FORM_ID_RE = re.compile(r"^([A-Z0-9]+)-(\d{4})([A-Z]\d+)$")


@dataclass
class Uppgift:
    code: str
    value: str

    @property
    def is_checkbox(self) -> bool:
        return self.value == "X"

    def as_int(self) -> int | None:
        if self.is_checkbox:
            return None
        try:
            return int(self.value)
        except ValueError:
            return None


@dataclass
class Blankett:
    form_id: str
    form_name: str
    year: int
    period: str
    identitet_orgnr: str | None = None
    identitet_date: str | None = None
    identitet_time: str | None = None
    namn: str | None = None
    systeminfo: str | None = None
    uppgifter: list[Uppgift] = field(default_factory=list)

    @classmethod
    def parse_form_id(cls, form_id: str) -> tuple[str, int, str]:
        match = _FORM_ID_RE.match(form_id)
        if not match:
            raise ValueError(f"Invalid form_id: {form_id!r}")
        form_name, year_str, period = match.groups()
        return form_name, int(year_str), period

    def get(self, code: str) -> str | None:
        for uppgift in self.uppgifter:
            if uppgift.code == code:
                return uppgift.value
        return None

    def get_all(self, code: str) -> list[str]:
        return [u.value for u in self.uppgifter if u.code == code]

    def __getitem__(self, code: str) -> str:
        value = self.get(code)
        if value is None:
            raise KeyError(code)
        return value

    def to_dict(self) -> dict[str, Any]:
        identitet: dict[str, str | None] | None = None
        if (
            self.identitet_orgnr is not None
            or self.identitet_date is not None
            or self.identitet_time is not None
        ):
            identitet = {
                "orgnr": self.identitet_orgnr,
                "date": self.identitet_date,
                "time": self.identitet_time,
            }
        return {
            "form_id": self.form_id,
            "form_name": self.form_name,
            "year": self.year,
            "period": self.period,
            "identitet": identitet,
            "namn": self.namn,
            "systeminfo": self.systeminfo,
            "uppgifter": [{"code": u.code, "value": u.value} for u in self.uppgifter],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Blankett:
        identitet = d.get("identitet")
        return cls(
            form_id=d["form_id"],
            form_name=d["form_name"],
            year=d["year"],
            period=d["period"],
            identitet_orgnr=identitet["orgnr"] if identitet else None,
            identitet_date=identitet["date"] if identitet else None,
            identitet_time=identitet["time"] if identitet else None,
            namn=d.get("namn"),
            systeminfo=d.get("systeminfo"),
            uppgifter=[Uppgift(code=u["code"], value=u["value"]) for u in d.get("uppgifter", [])],
        )


@dataclass
class SruFile:
    blanketter: list[Blankett] = field(default_factory=list)
    has_fil_slut: bool = False

    def find(self, form_name: str, year: int | None = None) -> list[Blankett]:
        return [
            b
            for b in self.blanketter
            if b.form_name.upper() == form_name.upper() and (year is None or b.year == year)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "has_fil_slut": self.has_fil_slut,
            "blanketter": [b.to_dict() for b in self.blanketter],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> SruFile:
        return cls(
            blanketter=[Blankett.from_dict(b) for b in d.get("blanketter", [])],
            has_fil_slut=d.get("has_fil_slut", False),
        )
