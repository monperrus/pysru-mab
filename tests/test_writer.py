from __future__ import annotations

from pathlib import Path

from pysru_mab._model import Blankett, SruFile, Uppgift
from pysru_mab._parser import parse, parse_file
from pysru_mab._writer import write, write_file

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestWrite:
    def test_uses_crlf(self) -> None:
        blankett = Blankett(
            form_id="INK2-2025P4",
            form_name="INK2",
            year=2025,
            period="P4",
            namn="Testbolaget AB",
            uppgifter=[Uppgift("7104", "57109")],
        )
        sru_file = SruFile(blanketter=[blankett], has_fil_slut=True)
        text = write(sru_file)
        assert "\r\n" in text
        assert "\n" not in text.replace("\r\n", "")

    def test_byte_identical_roundtrip_sample_blanketter(self) -> None:
        original = (FIXTURES_DIR / "sample_blanketter.sru").read_bytes()
        sru_file = parse(original.decode("ascii"))
        rewritten = write(sru_file).encode("ascii")
        assert rewritten == original

    def test_optional_fields_omitted_when_none(self) -> None:
        blankett = Blankett(form_id="INK2-2025P4", form_name="INK2", year=2025, period="P4")
        sru_file = SruFile(blanketter=[blankett])
        text = write(sru_file)
        lines = text.split("\r\n")
        assert lines == [
            "#BLANKETT INK2-2025P4",
            "#BLANKETTSLUT",
            "",
        ]

    def test_has_fil_slut_false_omits_fil_slut(self) -> None:
        blankett = Blankett(form_id="INK2-2025P4", form_name="INK2", year=2025, period="P4")
        sru_file = SruFile(blanketter=[blankett], has_fil_slut=False)
        text = write(sru_file)
        assert "#FIL_SLUT" not in text


class TestWriteFile:
    def test_roundtrip_with_cp850(self, tmp_path: Path) -> None:
        sru_file = parse_file(FIXTURES_DIR / "sample_blanketter_cp850.sru", encoding="cp850")

        out_path = tmp_path / "out.sru"
        write_file(sru_file, out_path, encoding="cp850")

        reparsed = parse_file(out_path, encoding="cp850")
        assert reparsed == sru_file

        original_bytes = (FIXTURES_DIR / "sample_blanketter_cp850.sru").read_bytes()
        rewritten_bytes = out_path.read_bytes()
        assert rewritten_bytes == original_bytes
