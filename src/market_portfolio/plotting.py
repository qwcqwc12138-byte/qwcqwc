from __future__ import annotations

import os
from pathlib import Path


def configure_matplotlib_cache() -> None:
    """Keep Matplotlib's cache inside the writable, git-ignored artifact directory."""
    cache_dir = Path.cwd() / "artifacts" / ".matplotlib"
    cache_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(cache_dir))
