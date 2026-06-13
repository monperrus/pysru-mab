# pysru-mab

A small Python library and CLI for working with **SRU files** — the file
format used by the Swedish Tax Agency (Skatteverket) for filing corporate
income tax declarations (INK2 and its appendices), as defined in the
[SKV 269](https://www.skatteverket.se/) technical specification.

## Why

A search of PyPI and GitHub turned up only **write-only** SRU encoders
(`pysru-accounting`, `K4Skatt`) — useful for *generating* an SRU file, but
nothing that *parses* an existing `BLANKETTER.SRU`/`INFO.SRU` file into
structured, semantically-labelled Python objects.

`pysru-mab` fills that gap:

- **Parse** `BLANKETTER.SRU` and `INFO.SRU` into typed Python objects.
- **Write** them back out, with byte-identical round-trip for unmodified
  data.
- **Look up** what a numeric field code (`7011`, `7104`, ...) actually
  means, via a small built-in code table for INK2/INK2R/INK2S.
- A `pysru-mab` CLI for converting SRU files to/from JSON.

## Install

```bash
pip install pysru-mab
```

## Quick start

```python
from pysru_mab import parse_file, describe

sru_file = parse_file("BLANKETTER.SRU")  # defaults to cp850 encoding

for blankett in sru_file.blanketter:
    print(blankett.form_id, blankett.namn)

    for uppgift in blankett.uppgifter:
        info = describe(blankett.form_name, uppgift.code)
        label = info["label"] if info else "?"
        print(f"  {uppgift.code} ({label}): {uppgift.value}")
```

Access individual fields:

```python
ink2 = sru_file.find("INK2")[0]
ink2.get("7104")        # -> "-67222" (or None if absent)
ink2.get_all("7104")    # -> all values for that code, in order
ink2["7104"]            # -> "-67222" (raises KeyError if absent)
```

## Writing / round-trip

```python
from pysru_mab import parse_file, write_file

sru_file = parse_file("BLANKETTER.SRU")
# ... modify sru_file.blanketter[...] ...
write_file(sru_file, "BLANKETTER_OUT.SRU")
```

`write_file` always emits CRLF line endings (as required by the SRU
format), regardless of the input. Unmodified files round-trip
byte-for-byte.

## INFO.SRU

`INFO.SRU` uses a different, nested-section format and has its own
parser/writer:

```python
from pysru_mab import parse_info_file, write_info_file

info = parse_info_file("INFO.SRU")
print(info.orgnr, info.namn)

write_info_file(info, "INFO_OUT.SRU")
```

## CLI usage

```bash
# Convert to JSON (optionally annotate fields with human-readable labels)
pysru-mab to-json BLANKETTER.SRU --describe -o blanketter.json

# Convert back to SRU
pysru-mab from-json blanketter.json -o BLANKETTER.SRU

# Look up what a field code means
pysru-mab describe INK2 7011
pysru-mab describe INK2          # list all known codes for a form

# INFO.SRU <-> JSON
pysru-mab info-to-json INFO.SRU -o info.json
pysru-mab info-from-json info.json -o INFO.SRU
```

If `-o`/`--output` is omitted, output goes to stdout.

## Code tables

`describe(form_name, code)` looks up a field code against the bundled
tables in `pysru_mab/data/` (`ink2.json`, `ink2r.json`, `ink2s.json`).
To add support for another form, drop in a new `data/<form>.json` file
with the schema:

```json
{
  "form": "INK2",
  "source": "SKV 269 (INK2, period 2025P4)",
  "codes": {
    "7011": {"label": "...", "description": "...", "field_type": "date"}
  }
}
```

`field_type` is one of `"amount"`, `"date"`, `"checkbox"`, `"text"`
(defaults to `"amount"`). You can also load a table from your own JSON
file at runtime with `load_custom_table(path)`.

**Status:** code tables are currently shipped for INK2, INK2R and INK2S
covering the fields most commonly used. Labels are best-effort based on
common SKV269/INK2 terminology — contributions and corrections against the
official SKV269 appendix are welcome. Other forms parse and write
correctly, but `describe()` returns `None` for them until a table is added.

## Format notes

- **Encoding**: SKV269 specifies CP850/IBM850. `cp850` is the default for
  all read/write functions, but it's configurable via the `encoding`
  keyword argument.
- **Line endings**: always CRLF (`\r\n`) on output.
- **Form IDs**: `#BLANKETT` lines use IDs like `INK2-2025P4`, parsed into
  `form_name="INK2"`, `year=2025`, `period="P4"`.
- **Values**: `#UPPGIFT` values are kept as raw strings to preserve sign,
  leading zeros, and the `"X"` checkbox marker; use `Uppgift.as_int()` /
  `Uppgift.is_checkbox` for typed access.

## License

MIT
