"""Entrypoint wrapper for `python scripts/teardown.py`."""

import sys
from pathlib import Path

# Make the teardown/ package importable when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent))

from teardown.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
