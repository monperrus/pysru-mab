from __future__ import annotations

from pathlib import Path

import pytest

from pysru_mab._model import Uppgift
from pysru_mab._parser import SruParseError, parse, parse_file

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseFullFile:
    def test_parses_all_blanketter(self) -> None:
        text = (FIXTURES_DIR / "sample_blanketter.sru").read_text()
        sru_file = parse(text)

        assert sru_file.has_fil_slut is True
        assert [b.form_id for b in sru_file.blanketter] == [
            "INK2-2025P4",
            "INK2R-2025P4",
            "INK2S-2025P4",
        ]

        ink2 = sru_file.blanketter[0]
        assert ink2.form_name == "INK2"
        assert ink2.year == 2025
        assert ink2.period == "P4"
        assert ink2.identitet_orgnr == "0000000000"
        assert ink2.identitet_date == "20260101"
        assert ink2.identitet_time == "120000"
        assert ink2.namn == "Testbolaget AB"
        assert ink2.systeminfo == "Test System 1.0"
        assert ink2.uppgifter == [
            Uppgift("7011", "20250101"),
            Uppgift("7012", "20251231"),
            Uppgift("7104", "-67222"),
            Uppgift("7650", "X"),
        ]

    def test_negative_numbers_and_checkbox_preserved(self) -> None:
        text = (FIXTURES_DIR / "sample_blanketter.sru").read_text()
        sru_file = parse(text)
        ink2 = sru_file.blanketter[0]
        assert ink2.get("7104") == "-67222"
        assert ink2.get("7650") == "X"
        uppgift = next(u for u in ink2.uppgifter if u.code == "7650")
        assert uppgift.is_checkbox is True


class TestParseErrors:
    def test_blankettslut_without_blankett(self) -> None:
        text = "#BLANKETTSLUT\r\n"
        with pytest.raises(SruParseError) as exc_info:
            parse(text)
        assert exc_info.value.line_no == 1
        assert "BLANKETTSLUT" in exc_info.value.line

    def test_unterminated_trailing_blankett(self) -> None:
        text = "#BLANKETT INK2-2025P4\r\n#NAMN Testbolaget AB\r\n"
        with pytest.raises(SruParseError, match="Unterminated"):
            parse(text)

    def test_fil_slut_with_unterminated_blankett(self) -> None:
        text = "#BLANKETT INK2-2025P4\r\n#FIL_SLUT\r\n"
        with pytest.raises(SruParseError, match="#FIL_SLUT"):
            parse(text)

    def test_malformed_uppgift_includes_line_number(self) -> None:
        text = (
            "#BLANKETT INK2-2025P4\r\n"
            "#UPPGIFT 7011\r\n"
            "#BLANKETTSLUT\r\n"
        )
        with pytest.raises(SruParseError) as exc_info:
            parse(text)
        assert exc_info.value.line_no == 2
        assert exc_info.value.line == "#UPPGIFT 7011"

    def test_unknown_keyword_strict_raises(self) -> None:
        text = "#BLANKETT INK2-2025P4\r\n#OKAND foo\r\n#BLANKETTSLUT\r\n"
        with pytest.raises(SruParseError, match="Unknown keyword"):
            parse(text, strict=True)

    def test_unknown_keyword_non_strict_ignored(self) -> None:
        text = "#BLANKETT INK2-2025P4\r\n#OKAND foo\r\n#BLANKETTSLUT\r\n"
        sru_file = parse(text, strict=False)
        assert len(sru_file.blanketter) == 1


class TestParseFile:
    def test_cp850_decodes_swedish_characters(self) -> None:
        sru_file = parse_file(FIXTURES_DIR / "sample_blanketter_cp850.sru", encoding="cp850")
        blankett = sru_file.blanketter[0]
        assert blankett.namn == "Åkerlunds Bokföring & Förvaltning AB"
        assert blankett.systeminfo == "Testprogram för bokföring 1.0"
