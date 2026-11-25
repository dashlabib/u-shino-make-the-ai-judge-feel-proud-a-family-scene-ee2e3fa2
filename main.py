#!/usr/bin/env python3
"""Make the AI Judge Feel Proud: A Family Scene.

Writes a one-line family scene to /output/entry.txt for the make.fun
bounty "Make the AI Judge Feel Proud: A Family Scene".

Gate (sealed scorer): /output/entry.txt must be UTF-8 text, 1-280
characters, not only whitespace, one or two lines, warm, funny and
heartfelt.

Standard library only. Deterministic: the same entry text is written
on every run.
"""

import argparse
import hashlib
import sys
import unicodedata
from pathlib import Path

ENTRY_TEXT = (
    "My daughter lost her first tooth and left it for the tooth fairy "
    "with a note: 'Payment due tonight. No excuses. Love, the boss of "
    "this house.' I have never been prouder of her negotiation skills."
)

MAX_CHARS = 280
MAX_LINES = 2
DEFAULT_OUTPUT = Path("/output/entry.txt")


def validate(text: str) -> None:
    """Validate entry text against the bounty gate.

    Raises ValueError on the first violated rule.
    """
    if not isinstance(text, str):
        raise ValueError("entry must be a string")
    # Must be valid UTF-8 when encoded.
    text.encode("utf-8")
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if len(text) < 1 or len(text) > MAX_CHARS:
        raise ValueError(
            f"entry must be 1-{MAX_CHARS} characters, got {len(text)}"
        )
    lines = text.split("\n")
    if len(lines) > MAX_LINES:
        raise ValueError(f"entry must be at most {MAX_LINES} lines, got {len(lines)}")
    if text != text.strip():
        raise ValueError("entry must not have leading or trailing whitespace")
    for line in lines:
        if line != line.rstrip():
            raise ValueError("entry line has trailing whitespace")
    for ch in text:
        # ASCII controls (other than newline/tab) and DEL.
        if ord(ch) < 0x20 and ch not in ("\n", "\t"):
            raise ValueError(f"entry contains control character U+{ord(ch):04X}")
        if ord(ch) == 0x7F:
            raise ValueError("entry contains DEL control character")
        if ch in ("\n", "\t"):
            continue
        # Any other Unicode control/format character (Cc, Cf), e.g.
        # zero-width joiners, bidi marks, or non-breaking spaces used
        # as invisible padding, are rejected too.
        if unicodedata.category(ch) in ("Cc", "Cf"):
            raise ValueError(
                f"entry contains Unicode control/format character U+{ord(ch):04X}"
            )
        if ch == "\u00a0":
            raise ValueError("entry contains a non-breaking space")
    if "  " in text:
        raise ValueError("entry contains a double space")


def write_entry(output: Path) -> Path:
    """Validate and write the entry text (no trailing newline)."""
    validate(ENTRY_TEXT)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(ENTRY_TEXT.encode("utf-8"))
    return output


def self_test() -> int:
    """Verify the entry and determinism; print PASS on success."""
    validate(ENTRY_TEXT)
    digest = hashlib.sha256(ENTRY_TEXT.encode("utf-8")).hexdigest()
    tmp_a = Path("/tmp/entry-self-test-a.txt")
    tmp_b = Path("/tmp/entry-self-test-b.txt")
    write_entry(tmp_a)
    write_entry(tmp_b)
    a = tmp_a.read_bytes()
    b = tmp_b.read_bytes()
    if a != b:
        print("FAIL: two consecutive runs differ")
        return 1
    if hashlib.sha256(a).hexdigest() != digest:
        print("FAIL: output hash does not match entry text")
        return 1
    print(
        f"PASS: entry is {len(ENTRY_TEXT)} characters "
        f"(gate: 1-{MAX_CHARS} chars, max {MAX_LINES} lines), "
        f"sha256={digest}, two consecutive runs byte-identical"
    )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="where to write entry.txt (default: /output/entry.txt)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="validate the entry and check determinism instead of writing",
    )
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    out = write_entry(args.output)
    print(f"Wrote {len(ENTRY_TEXT)} characters to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
