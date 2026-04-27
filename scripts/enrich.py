"""Entrypoint wrapper for `python scripts/enrich.py`."""

import sys
from pathlib import Path

# Make the enrich/ package importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from enrich.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
