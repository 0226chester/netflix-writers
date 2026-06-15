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

from .const import DB_DIR, DB_PATH
from .lib import cleanup, fetch_url

BASE_URL = "https://datasets.imdbws.com"
IMDB_DIR = os.path.join(DB_DIR, "imdb")
IMDB_TITLE_TYPES = ["movie", "tvSeries", "tvMiniSeries"]


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
        f""" # nosec B608
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
        with duckdb.connect(DB_PATH) as con:
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
        with duckdb.connect(DB_PATH) as con:
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
