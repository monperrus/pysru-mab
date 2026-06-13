from __future__ import annotations

import pytest

from pysru_mab._model import Blankett, SruFile, Uppgift


class TestUppgift:
    def test_is_checkbox(self) -> None:
        assert Uppgift("7012", "X").is_checkbox is True
        assert Uppgift("7012", "57109").is_checkbox is False

    def test_as_int(self) -> None:
        assert Uppgift("7104", "57109").as_int() == 57109
        assert Uppgift("7104", "-67222").as_int() == -67222
        assert Uppgift("7012", "X").as_int() is None
        assert Uppgift("7011", "20250101").as_int() == 20250101


class TestBlankettParseFormId:
    def test_ink2(self) -> None:
        assert Blankett.parse_form_id("INK2-2025P4") == ("INK2", 2025, "P4")

    def test_ink2r(self) -> None:
        assert Blankett.parse_form_id("INK2R-2025P4") == ("INK2R", 2025, "P4")

    def test_ink2s(self) -> None:
        assert Blankett.parse_form_id("INK2S-2025P4") == ("INK2S", 2025, "P4")

    def test_invalid(self) -> None:
        with pytest.raises(ValueError, match="Invalid form_id"):
            Blankett.parse_form_id("not-a-form-id")


@pytest.fixture
def blankett() -> Blankett:
    return Blankett(
        form_id="INK2-2025P4",
        form_name="INK2",
        year=2025,
        period="P4",
        identitet_orgnr="0000000000",
        identitet_date="20260101",
        identitet_time="120000",
        namn="Test AB",
        systeminfo="Test System 1.0",
        uppgifter=[
            Uppgift("7011", "20250101"),
            Uppgift("7012", "20251231"),
            Uppgift("7104", "-67222"),
            Uppgift("7104", "57109"),
        ],
    )


class TestBlankettAccess:
    def test_get_returns_first_match(self, blankett: Blankett) -> None:
        assert blankett.get("7104") == "-67222"

    def test_get_missing_returns_none(self, blankett: Blankett) -> None:
        assert blankett.get("9999") is None

    def test_get_all_returns_all_matches(self, blankett: Blankett) -> None:
        assert blankett.get_all("7104") == ["-67222", "57109"]

    def test_get_all_missing_returns_empty(self, blankett: Blankett) -> None:
        assert blankett.get_all("9999") == []

    def test_getitem(self, blankett: Blankett) -> None:
        assert blankett["7011"] == "20250101"

    def test_getitem_missing_raises_keyerror(self, blankett: Blankett) -> None:
        with pytest.raises(KeyError):
            blankett["9999"]


class TestBlankettDictRoundtrip:
    def test_to_dict_from_dict(self, blankett: Blankett) -> None:
        d = blankett.to_dict()
        assert d["form_id"] == "INK2-2025P4"
        assert d["identitet"] == {
            "orgnr": "0000000000",
            "date": "20260101",
            "time": "120000",
        }
        assert Blankett.from_dict(d) == blankett

    def test_to_dict_identitet_none(self) -> None:
        b = Blankett(form_id="INK2-2025P4", form_name="INK2", year=2025, period="P4")
        d = b.to_dict()
        assert d["identitet"] is None
        assert Blankett.from_dict(d) == b


class TestSruFile:
    def test_find_by_form_name(self, blankett: Blankett) -> None:
        other = Blankett(form_id="INK2R-2025P4", form_name="INK2R", year=2025, period="P4")
        sru_file = SruFile(blanketter=[blankett, other], has_fil_slut=True)
        assert sru_file.find("INK2") == [blankett]
        assert sru_file.find("ink2") == [blankett]
        assert sru_file.find("INK2R") == [other]
        assert sru_file.find("INK2", year=2025) == [blankett]
        assert sru_file.find("INK2", year=2024) == []
        assert sru_file.find("UNKNOWN") == []

    def test_to_dict_from_dict(self, blankett: Blankett) -> None:
        sru_file = SruFile(blanketter=[blankett], has_fil_slut=True)
        d = sru_file.to_dict()
        assert d["has_fil_slut"] is True
        assert SruFile.from_dict(d) == sru_file
