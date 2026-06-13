from __future__ import annotations

import argparse
import contextlib
import json
import sys
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any, TextIO

from pysru_mab._codes import available_forms, codes_for_form, describe
from pysru_mab._info import InfoSru, parse_info_file, write_info, write_info_file
from pysru_mab._model import Blankett, SruFile, Uppgift
from pysru_mab._parser import SruParseError, parse_file
from pysru_mab._writer import write, write_file


def _open_output(path: str | None) -> AbstractContextManager[TextIO]:
    if path is None:
        return contextlib.nullcontext(sys.stdout)
    return open(path, "w", encoding="utf-8")


def _uppgift_to_json(uppgift: Uppgift, form_name: str, describe_codes: bool) -> dict[str, Any]:
    entry: dict[str, Any] = {"code": uppgift.code, "value": uppgift.value}
    if describe_codes:
        info = describe(form_name, uppgift.code)
        if info is not None:
            entry["label"] = info["label"]
            entry["description"] = info["description"]
    return entry


def _blankett_to_json(blankett: Blankett, describe_codes: bool) -> dict[str, Any]:
    d = blankett.to_dict()
    d["uppgifter"] = [
        _uppgift_to_json(u, blankett.form_name, describe_codes) for u in blankett.uppgifter
    ]
    return d


def cmd_to_json(args: argparse.Namespace) -> int:
    sru_file = parse_file(args.input, encoding=args.encoding)
    data = {
        "has_fil_slut": sru_file.has_fil_slut,
        "blanketter": [_blankett_to_json(b, args.describe) for b in sru_file.blanketter],
    }
    with _open_output(args.output) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


def cmd_from_json(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    sru_file = SruFile.from_dict(data)
    if args.output is None:
        sys.stdout.write(write(sru_file))
    else:
        write_file(sru_file, args.output, encoding=args.encoding)
    return 0


def cmd_describe(args: argparse.Namespace) -> int:
    form = args.form.upper()
    if form not in available_forms():
        print(f"Unknown form: {args.form}", file=sys.stderr)
        return 1

    if args.code is None:
        table = codes_for_form(form)
        assert table is not None
        for code, code_info in sorted(table.items()):
            print(f"{code}\t{code_info['label']}\t({code_info['field_type']})")
        return 0

    info = describe(form, args.code)
    if info is None:
        print(f"Unknown code {args.code!r} for form {form}", file=sys.stderr)
        return 1
    print(f"{args.code}\t{info['label']}\t({info['field_type']})")
    print(info["description"])
    return 0


def cmd_info_to_json(args: argparse.Namespace) -> int:
    info = parse_info_file(args.input, encoding=args.encoding)
    data = {
        "produkt": info.produkt,
        "skapad_date": info.skapad_date,
        "skapad_time": info.skapad_time,
        "program": info.program,
        "filnamn": info.filnamn,
        "orgnr": info.orgnr,
        "namn": info.namn,
        "adress": info.adress,
        "postnr": info.postnr,
        "postort": info.postort,
    }
    with _open_output(args.output) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


def cmd_info_from_json(args: argparse.Namespace) -> int:
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    info = InfoSru(**data)
    if args.output is None:
        sys.stdout.write(write_info(info))
    else:
        write_info_file(info, args.output, encoding=args.encoding)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pysru-mab")
    subparsers = parser.add_subparsers(dest="command", required=True)

    to_json = subparsers.add_parser("to-json", help="Convert a BLANKETTER.SRU file to JSON")
    to_json.add_argument("input")
    to_json.add_argument("-o", "--output")
    to_json.add_argument("--encoding", default="cp850")
    to_json.add_argument("--describe", action="store_true")
    to_json.set_defaults(func=cmd_to_json)

    from_json = subparsers.add_parser(
        "from-json", help="Convert JSON back to a BLANKETTER.SRU file"
    )
    from_json.add_argument("input")
    from_json.add_argument("-o", "--output")
    from_json.add_argument("--encoding", default="cp850")
    from_json.set_defaults(func=cmd_from_json)

    describe_parser = subparsers.add_parser("describe", help="Look up a field code's label")
    describe_parser.add_argument("form")
    describe_parser.add_argument("code", nargs="?")
    describe_parser.set_defaults(func=cmd_describe)

    info_to_json = subparsers.add_parser("info-to-json", help="Convert an INFO.SRU file to JSON")
    info_to_json.add_argument("input")
    info_to_json.add_argument("-o", "--output")
    info_to_json.add_argument("--encoding", default="cp850")
    info_to_json.set_defaults(func=cmd_info_to_json)

    info_from_json = subparsers.add_parser(
        "info-from-json", help="Convert JSON back to an INFO.SRU file"
    )
    info_from_json.add_argument("input")
    info_from_json.add_argument("-o", "--output")
    info_from_json.add_argument("--encoding", default="cp850")
    info_from_json.set_defaults(func=cmd_info_from_json)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func: Callable[[argparse.Namespace], int] = args.func
    try:
        return func(args)
    except SruParseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
