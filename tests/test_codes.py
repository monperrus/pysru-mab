from __future__ import annotations

from pathlib import Path

from pysru_mab._codes import available_forms, describe, load_custom_table

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestDescribe:
    def test_known_code(self) -> None:
        info = describe("INK2", "7011")
        assert info is not None
        assert info["label"] == "Räkenskapsår, från"
        assert info["field_type"] == "date"

    def test_case_insensitive_form_name(self) -> None:
        assert describe("ink2", "7011") == describe("INK2", "7011")

    def test_unknown_code_returns_none(self) -> None:
        assert describe("INK2", "9999") is None

    def test_unknown_form_returns_none(self) -> None:
        assert describe("NOPE", "7011") is None


class TestAvailableForms:
    def test_includes_seeded_forms(self) -> None:
        forms = available_forms()
        assert "INK2" in forms
        assert "INK2R" in forms
        assert "INK2S" in forms


class TestLoadCustomTable:
    def test_loads_custom_codes(self) -> None:
        table = load_custom_table(str(FIXTURES_DIR / "custom_codes.json"))
        assert "INK2X" in table
        assert table["INK2X"]["9999"]["label"] == "Test code"
