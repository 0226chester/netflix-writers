"""Utility functions for downloading and managing files."""

import json
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm


def fetch_url(url: str, output_dir: str | Path, timeout: int = 60) -> Path | None:
    """
    Download a file and return its local path.

    Args:
        url: URL to download.
        output_dir: Directory where the file will be saved.
        timeout: HTTP timeout in seconds.

    Returns:
        Path to the downloaded file, or None if the download fails.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = url.rsplit("/", maxsplit=1)[-1]
    output_path = output_dir / filename
    if output_path.exists():
        print(f"File {output_path} already exists, skipping download.")
        return output_path

    # Reuse an existing download.
    if output_path.exists():
        print(f"File {output_path} already exists, skipping download.")
        return output_path

    try:
        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))

            with output_path.open("wb") as fp:
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=filename,
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                        if chunk:
                            fp.write(chunk)
                            pbar.update(len(chunk))

    except (requests.RequestException, OSError) as exc:
        print(f"Failed to download {url}: {exc}")

        # Avoid leaving behind a partial download.
        output_path.unlink(missing_ok=True)

        return None

    return output_path


def cleanup(filename: Path) -> None:
    """Delete a file if it exists."""
    try:
        filename.unlink(missing_ok=True)
    except OSError as exc:
        print(f"Failed to remove {filename}: {exc}")


def safe_cast(x) -> list:
    """
    Always returns a list safely, even if input is:

    - NaN
    - list
    - dict
    - malformed JSON string
    - numpy array
    """
    if x is None:
        return []

    # already list-like
    if isinstance(x, list):
        return x

    if isinstance(x, tuple):
        return list(x)

    # pandas NaN safe check
    try:
        if pd.isna(x):
            return []
    # pylint: disable=broad-except
    except Exception:
        pass

    if isinstance(x, str):
        try:
            parsed = json.loads(x)
            if isinstance(parsed, list):
                return [c.get("name") for c in parsed if isinstance(c, dict) and "name" in c]
            return []
        # pylint: disable=broad-except
        except Exception:
            return []

    return []
