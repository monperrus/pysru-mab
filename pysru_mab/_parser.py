from __future__ import annotations

from pathlib import Path

from pysru_mab._model import Blankett, SruFile, Uppgift

DEFAULT_ENCODING = "cp850"


class SruParseError(ValueError):
    def __init__(self, message: str, line_no: int, line: str) -> None:
        super().__init__(f"{message} (line {line_no}: {line!r})")
        self.line_no = line_no
        self.line = line


def parse(text: str, *, strict: bool = True) -> SruFile:
    sru_file = SruFile()
    current: Blankett | None = None
    line_no = 0
    line = ""

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\r\n")
        if not line:
            continue
        if not line.startswith("#"):
            raise SruParseError("Expected line starting with '#'", line_no, line)

        parts = line.split(maxsplit=1)
        keyword = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if keyword == "#BLANKETT":
            if current is not None:
                raise SruParseError(
                    "Nested #BLANKETT without preceding #BLANKETTSLUT", line_no, line
                )
            form_id = rest.strip()
            form_name, year, period = Blankett.parse_form_id(form_id)
            current = Blankett(form_id=form_id, form_name=form_name, year=year, period=period)
        elif keyword == "#IDENTITET":
            if current is None:
                raise SruParseError("#IDENTITET outside of #BLANKETT block", line_no, line)
            tokens = rest.split()
            if len(tokens) != 3:
                raise SruParseError("#IDENTITET requires exactly 3 fields", line_no, line)
            current.identitet_orgnr, current.identitet_date, current.identitet_time = tokens
        elif keyword == "#NAMN":
            if current is None:
                raise SruParseError("#NAMN outside of #BLANKETT block", line_no, line)
            current.namn = rest
        elif keyword == "#SYSTEMINFO":
            if current is None:
                raise SruParseError("#SYSTEMINFO outside of #BLANKETT block", line_no, line)
            current.systeminfo = rest
        elif keyword == "#UPPGIFT":
            if current is None:
                raise SruParseError("#UPPGIFT outside of #BLANKETT block", line_no, line)
            tokens = rest.split()
            if len(tokens) != 2:
                raise SruParseError("#UPPGIFT requires exactly 2 fields", line_no, line)
            current.uppgifter.append(Uppgift(code=tokens[0], value=tokens[1]))
        elif keyword == "#BLANKETTSLUT":
            if current is None:
                raise SruParseError("#BLANKETTSLUT without matching #BLANKETT", line_no, line)
            sru_file.blanketter.append(current)
            current = None
        elif keyword == "#FIL_SLUT":
            if current is not None:
                raise SruParseError(
                    "#FIL_SLUT with unterminated #BLANKETT block", line_no, line
                )
            sru_file.has_fil_slut = True
        else:
            if strict:
                raise SruParseError(f"Unknown keyword {keyword!r}", line_no, line)

    if current is not None:
        raise SruParseError("Unterminated #BLANKETT block at end of file", line_no, line)

    return sru_file


def parse_file(
    path: str | Path, *, encoding: str = DEFAULT_ENCODING, strict: bool = True
) -> SruFile:
    text = Path(path).read_text(encoding=encoding)
    return parse(text, strict=strict)
