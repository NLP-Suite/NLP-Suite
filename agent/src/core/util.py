import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)


def safe_read_csv(path: str, cols: Optional[list] = None) -> pd.DataFrame:
    """Read a CSV with utf-8 fallback to ISO-8859-1."""
    kwargs: dict = {"on_bad_lines": "skip"}
    if cols is not None:
        kwargs["usecols"] = cols
    try:
        return pd.read_csv(path, encoding="utf-8", **kwargs)
    except UnicodeDecodeError:
        logger.info(f"utf-8 failed for {path}, retrying with ISO-8859-1")
        try:
            return pd.read_csv(path, encoding="ISO-8859-1", **kwargs)
        except Exception as e:
            raise ValueError(f"Could not read CSV {path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Could not read CSV {path}: {e}") from e


def collect(results: list, item: Optional[object] = None) -> None:
    """Append a str or extend a list into results, ignoring None."""
    if item is None:
        return
    if isinstance(item, str):
        results.append(item)
    else:
        results.extend(item)


def output_path(*parts: str) -> str:
    """Join path parts — drop-in replacement for outputDir + os.sep + filename."""
    return os.path.join(*parts)
