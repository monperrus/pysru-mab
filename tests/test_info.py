from __future__ import annotations

from pathlib import Path

from pysru_mab._info import InfoSru, parse_info, parse_info_file, write_info, write_info_file

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseInfo:
    def test_parses_fields(self) -> None:
        text = (FIXTURES_DIR / "sample_info.sru").read_text()
        info = parse_info(text)

        assert info == InfoSru(
            produkt="SRU",
            skapad_date="20260101",
            skapad_time="120000",
            program="Test System 1.0",
            filnamn="blanketter.sru",
            orgnr="0000000000",
            namn="Testbolaget AB",
            adress="Testgatan 1",
            postnr="12345",
            postort="Teststad",
        )


class TestWriteInfo:
    def test_byte_identical_roundtrip(self) -> None:
        original = (FIXTURES_DIR / "sample_info.sru").read_bytes()
        info = parse_info(original.decode("ascii"))
        rewritten = write_info(info).encode("ascii")
        assert rewritten == original

    def test_optional_fields_omitted(self) -> None:
        text = write_info(InfoSru())
        assert "#PRODUKT" not in text
        assert "#ORGNR" not in text
        assert "#DATABESKRIVNING_START" in text
        assert "#MEDIELEV_SLUT" in text


class TestFileRoundtrip:
    def test_parse_write_file_cp850(self, tmp_path: Path) -> None:
        info = parse_info_file(FIXTURES_DIR / "sample_info.sru", encoding="cp850")

        out_path = tmp_path / "info_out.sru"
        write_info_file(info, out_path, encoding="cp850")

        reparsed = parse_info_file(out_path, encoding="cp850")
        assert reparsed == info

        original_bytes = (FIXTURES_DIR / "sample_info.sru").read_bytes()
        assert out_path.read_bytes() == original_bytes
