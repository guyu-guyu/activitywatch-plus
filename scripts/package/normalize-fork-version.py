"""Let fork tags such as v0.14.4b1-plus.1 survive aw-server packaging.

aw-server's package step passes the git tag to ``poetry version``. PEP 440
rejects ``0.14.4b1-plus.1``; ``0.14.4b1+plus.1`` is the same tag expressed as
a local version. The rewrite is applied to the aw-server Makefile in the
checkout and is not committed back to that submodule.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = ROOT / "aw-server" / "Makefile"
OLD = "poetry version $$VERSION"
NEW = (
    'poetry version "$$(printf %s "$$VERSION" | sed -E \'s/-plus[.]/+plus./\')"'
)


def main() -> int:
    text = MAKEFILE.read_text(encoding="utf-8")
    if NEW in text:
        print("aw-server package version is already PEP 440 safe")
        return 0
    if OLD not in text:
        print(f"Could not find the poetry version line in {MAKEFILE}", file=sys.stderr)
        return 1
    MAKEFILE.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("aw-server will package -plus.N tags as +plus.N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
