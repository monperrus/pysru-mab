from __future__ import annotations

from pathlib import Path

from pysru_mab._model import SruFile

LINE_ENDING = "\r\n"


def write(sru_file: SruFile) -> str:
    lines: list[str] = []
    for blankett in sru_file.blanketter:
        lines.append(f"#BLANKETT {blankett.form_id}")
        if (
            blankett.identitet_orgnr is not None
            or blankett.identitet_date is not None
            or blankett.identitet_time is not None
        ):
            lines.append(
                f"#IDENTITET {blankett.identitet_orgnr} "
                f"{blankett.identitet_date} {blankett.identitet_time}"
            )
        if blankett.namn is not None:
            lines.append(f"#NAMN {blankett.namn}")
        if blankett.systeminfo is not None:
            lines.append(f"#SYSTEMINFO {blankett.systeminfo}")
        for uppgift in blankett.uppgifter:
            lines.append(f"#UPPGIFT {uppgift.code} {uppgift.value}")
        lines.append("#BLANKETTSLUT")

    if sru_file.has_fil_slut:
        lines.append("#FIL_SLUT")

    return LINE_ENDING.join(lines) + LINE_ENDING if lines else ""


def write_file(sru_file: SruFile, path: str | Path, *, encoding: str = "cp850") -> None:
    text = write(sru_file)
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(text)
