from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pysru_mab._parser import SruParseError

LINE_ENDING = "\r\n"
DEFAULT_ENCODING = "cp850"


@dataclass
class InfoSru:
    produkt: str | None = None
    skapad_date: str | None = None
    skapad_time: str | None = None
    program: str | None = None
    filnamn: str | None = None
    orgnr: str | None = None
    namn: str | None = None
    adress: str | None = None
    postnr: str | None = None
    postort: str | None = None


def parse_info(text: str) -> InfoSru:
    info = InfoSru()

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\r\n")
        if not line:
            continue

        parts = line.split(maxsplit=1)
        keyword = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        if keyword in ("#DATABESKRIVNING_START", "#DATABESKRIVNING_SLUT",
                       "#MEDIELEV_START", "#MEDIELEV_SLUT"):
            continue
        elif keyword == "#PRODUKT":
            info.produkt = rest
        elif keyword == "#SKAPAD":
            tokens = rest.split()
            if len(tokens) != 2:
                raise SruParseError("#SKAPAD requires exactly 2 fields", line_no, line)
            info.skapad_date, info.skapad_time = tokens
        elif keyword == "#PROGRAM":
            info.program = rest
        elif keyword == "#FILNAMN":
            info.filnamn = rest
        elif keyword == "#ORGNR":
            info.orgnr = rest
        elif keyword == "#NAMN":
            info.namn = rest
        elif keyword == "#ADRESS":
            info.adress = rest
        elif keyword == "#POSTNR":
            info.postnr = rest
        elif keyword == "#POSTORT":
            info.postort = rest
        else:
            raise SruParseError(f"Unknown keyword {keyword!r}", line_no, line)

    return info


def parse_info_file(path: str | Path, *, encoding: str = DEFAULT_ENCODING) -> InfoSru:
    text = Path(path).read_text(encoding=encoding)
    return parse_info(text)


def write_info(info: InfoSru) -> str:
    lines: list[str] = ["#DATABESKRIVNING_START"]
    if info.produkt is not None:
        lines.append(f"#PRODUKT {info.produkt}")
    if info.skapad_date is not None or info.skapad_time is not None:
        lines.append(f"#SKAPAD {info.skapad_date} {info.skapad_time}")
    if info.program is not None:
        lines.append(f"#PROGRAM {info.program}")
    if info.filnamn is not None:
        lines.append(f"#FILNAMN {info.filnamn}")
    lines.append("#DATABESKRIVNING_SLUT")

    lines.append("#MEDIELEV_START")
    if info.orgnr is not None:
        lines.append(f"#ORGNR {info.orgnr}")
    if info.namn is not None:
        lines.append(f"#NAMN {info.namn}")
    if info.adress is not None:
        lines.append(f"#ADRESS {info.adress}")
    if info.postnr is not None:
        lines.append(f"#POSTNR {info.postnr}")
    if info.postort is not None:
        lines.append(f"#POSTORT {info.postort}")
    lines.append("#MEDIELEV_SLUT")

    return LINE_ENDING.join(lines) + LINE_ENDING


def write_info_file(info: InfoSru, path: str | Path, *, encoding: str = DEFAULT_ENCODING) -> None:
    text = write_info(info)
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(text)
