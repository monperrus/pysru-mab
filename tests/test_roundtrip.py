from __future__ import annotations

from pathlib import Path

from pysru_mab._model import SruFile
from pysru_mab._parser import parse
from pysru_mab._writer import write

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestParseWriteRoundtrip:
    def test_sample_blanketter(self) -> None:
        text = (FIXTURES_DIR / "sample_blanketter.sru").read_text()
        sru_file = parse(text)
        assert parse(write(sru_file)) == sru_file

    def test_sample_blanketter_cp850(self) -> None:
        text = (FIXTURES_DIR / "sample_blanketter_cp850.sru").read_bytes().decode("cp850")
        sru_file = parse(text)
        assert parse(write(sru_file)) == sru_file


class TestDictRoundtrip:
    def test_sample_blanketter(self) -> None:
        text = (FIXTURES_DIR / "sample_blanketter.sru").read_text()
        sru_file = parse(text)
        assert SruFile.from_dict(sru_file.to_dict()) == sru_file
