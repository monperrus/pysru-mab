from __future__ import annotations

import json
from pathlib import Path

import pytest

from pysru_mab._cli import main
from pysru_mab._parser import parse_file

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestToJson:
    def test_to_json_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["to-json", str(FIXTURES_DIR / "sample_blanketter.sru"), "--encoding", "ascii"])
        out = capsys.readouterr().out
        data = json.loads(out)
        assert data["has_fil_slut"] is True
        assert data["blanketter"][0]["form_id"] == "INK2-2025P4"
        assert "label" not in data["blanketter"][0]["uppgifter"][0]

    def test_to_json_with_describe(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(
            [
                "to-json",
                str(FIXTURES_DIR / "sample_blanketter.sru"),
                "--encoding",
                "ascii",
                "--describe",
            ]
        )
        out = capsys.readouterr().out
        data = json.loads(out)
        uppgift_7011 = data["blanketter"][0]["uppgifter"][0]
        assert uppgift_7011["code"] == "7011"
        assert uppgift_7011["label"] == "Räkenskapsår, från"

    def test_to_json_output_file(self, tmp_path: Path) -> None:
        out_path = tmp_path / "out.json"
        main(
            [
                "to-json",
                str(FIXTURES_DIR / "sample_blanketter.sru"),
                "--encoding",
                "ascii",
                "-o",
                str(out_path),
            ]
        )
        data = json.loads(out_path.read_text())
        assert data["has_fil_slut"] is True


class TestFromJson:
    def test_roundtrip(self, tmp_path: Path) -> None:
        sru_file = parse_file(FIXTURES_DIR / "sample_blanketter.sru", encoding="ascii")
        json_path = tmp_path / "in.json"
        json_path.write_text(json.dumps(sru_file.to_dict(), ensure_ascii=False))

        sru_path = tmp_path / "out.sru"
        main(["from-json", str(json_path), "-o", str(sru_path), "--encoding", "ascii"])

        reparsed = parse_file(sru_path, encoding="ascii")
        assert reparsed == sru_file

    def test_from_json_stdout(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        sru_file = parse_file(FIXTURES_DIR / "sample_blanketter.sru", encoding="ascii")
        json_path = tmp_path / "in.json"
        json_path.write_text(json.dumps(sru_file.to_dict(), ensure_ascii=False))

        main(["from-json", str(json_path)])
        out = capsys.readouterr().out
        assert "#BLANKETT INK2-2025P4" in out


class TestDescribe:
    def test_describe_form_and_code(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["describe", "INK2", "7011"])
        out = capsys.readouterr().out
        assert "Räkenskapsår, från" in out

    def test_describe_form_only_lists_codes(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["describe", "INK2"])
        out = capsys.readouterr().out
        assert "7011" in out
        assert "7104" in out

    def test_describe_unknown_form_exit_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        ret = main(["describe", "NOPE"])
        assert ret == 1
        err = capsys.readouterr().err
        assert "Unknown form" in err

    def test_describe_unknown_code_exit_1(self, capsys: pytest.CaptureFixture[str]) -> None:
        ret = main(["describe", "INK2", "9999"])
        assert ret == 1
        err = capsys.readouterr().err
        assert "Unknown code" in err


class TestInfoJson:
    def test_info_to_json_and_back(self, tmp_path: Path) -> None:
        json_path = tmp_path / "info.json"
        main(
            [
                "info-to-json",
                str(FIXTURES_DIR / "sample_info.sru"),
                "--encoding",
                "ascii",
                "-o",
                str(json_path),
            ]
        )
        data = json.loads(json_path.read_text())
        assert data["orgnr"] == "0000000000"

        sru_path = tmp_path / "info_out.sru"
        main(["info-from-json", str(json_path), "-o", str(sru_path), "--encoding", "ascii"])
        assert sru_path.read_bytes() == (FIXTURES_DIR / "sample_info.sru").read_bytes()
