from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from pysru_mab._codes import available_forms, describe
from pysru_mab._info import InfoSru, parse_info, parse_info_file, write_info, write_info_file
from pysru_mab._model import Blankett, SruFile, Uppgift
from pysru_mab._parser import SruParseError, parse, parse_file
from pysru_mab._writer import write, write_file

try:
    __version__ = version("pysru-mab")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "Blankett",
    "InfoSru",
    "SruFile",
    "SruParseError",
    "Uppgift",
    "__version__",
    "available_forms",
    "describe",
    "parse",
    "parse_file",
    "parse_info",
    "parse_info_file",
    "write",
    "write_file",
    "write_info",
    "write_info_file",
]
