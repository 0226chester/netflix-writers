"""
Download and prune IMDb datasets.

This script downloads IMDb's title.basics and title.ratings datasets,
filters them to retain only non-adult movies, TV series, and TV mini-series,
and exports the results to CSV files.

Outputs:
    - titles.basics.csv
    - title.ratings.csv
"""

import os
from pathlib import Path

import duckdb
import requests
from tqdm import tqdm

BASE_URL = "https://datasets.imdbws.com"
HERE = os.path.abspath(os.path.dirname(__file__))
DB_DIR = os.path.join(HERE, "db")
IMDB_DIR = os.path.join(DB_DIR, "imdb")

DUCKDB_PATH = os.path.join(IMDB_DIR, "imdb.duckdb")
IMDB_TITLE_TYPES = ["movie", "tvSeries", "tvMiniSeries"]


def fetch_url(url: str, output_dir: str | Path = IMDB_DIR, timeout: int = 60) -> Path | None:
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


def export_titles(con: duckdb.DuckDBPyConnection) -> None:
    """Export the filtered titles table to titles.basics.csv."""
    output_path = os.path.join(IMDB_DIR, "titles.basics.csv")
    con.execute(f"""
        COPY title_basics
        TO '{output_path}'
        (FORMAT csv, HEADER true)
        """)
    print(f"Exported title_basics to {output_path}.")


def export_ratings(con: duckdb.DuckDBPyConnection) -> None:
    """Export the filtered ratings table to title.ratings.csv."""
    output_path = os.path.join(IMDB_DIR, "title.ratings.csv")
    con.execute(f"""
        COPY title_ratings
        TO '{output_path}'
        (FORMAT csv, HEADER true)
        """)
    print(f"Exported title_ratings to {output_path}.")


def build_titles_table(con: duckdb.DuckDBPyConnection, filename: Path) -> None:
    """Create the filtered titles table."""
    print(f"Building title_basics table from {filename}...")
    title_types = ", ".join(f"'{t}'" for t in IMDB_TITLE_TYPES)
    con.execute(
        f"""
        CREATE OR REPLACE TABLE title_basics AS
        SELECT  *
        FROM    read_csv_auto(?, delim='\t')
        WHERE   titleType IN ({title_types}) AND
                isAdult = '0'
        """,
        [str(filename)],
    )
    print("built title_basics table.")


def build_ratings_table(con: duckdb.DuckDBPyConnection, filename: Path) -> None:
    """Create the filtered ratings table corresponding to titles."""
    print(f"Building title_ratings table from {filename}...")
    con.execute(
        """
        CREATE OR REPLACE TABLE title_ratings AS
        SELECT  r.*
        FROM    read_csv_auto(?, delim='\t') AS r
                SEMI JOIN title_basics USING (tconst)
        """,
        [str(filename)],
    )
    print("built title_ratings table.")


def fetch_title_basics(with_cleanup: bool = False) -> None:
    titles_url = f"{BASE_URL}/title.basics.tsv.gz"
    titles_file: Path | None

    titles_file = fetch_url(titles_url, output_dir=IMDB_DIR)

    if titles_file is None:
        raise RuntimeError("Failed to download title.basics.tsv.gz")

    try:
        with duckdb.connect(DUCKDB_PATH) as con:
            build_titles_table(con, titles_file)
            export_titles(con)

    finally:
        if with_cleanup:
            cleanup(titles_file)

    print("Generated titles.basics.csv")
    print("-" * 40)


def fetch_title_ratings(with_cleanup: bool = False) -> None:
    ratings_url = f"{BASE_URL}/title.ratings.tsv.gz"
    ratings_file: Path | None

    ratings_file = fetch_url(ratings_url, output_dir=IMDB_DIR)

    if ratings_file is None:
        raise RuntimeError("Failed to download title.ratings.tsv.gz")

    try:
        with duckdb.connect(DUCKDB_PATH) as con:
            build_ratings_table(con, ratings_file)
            export_ratings(con)

    finally:
        if with_cleanup:
            cleanup(ratings_file)

    print("Generated title.ratings.csv")
    print("-" * 40)


def main() -> None:
    """Download, prune, export, and clean up IMDb datasets."""
    fetch_title_basics()
    fetch_title_ratings()


if __name__ == "__main__":
    main()
