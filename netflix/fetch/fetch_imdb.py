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

from .const import DB_DIR, DB_FILE
from .lib import cleanup, fetch_url

BASE_URL = "https://datasets.imdbws.com"
IMDB_DIR = os.path.join(DB_DIR, "imdb")
IMDB_TITLE_TYPES = ["movie", "tvSeries"]


def export_titles(con: duckdb.DuckDBPyConnection) -> None:
    """
    Export the filtered titles table to titles.basics.csv.

    .. args:
        con: A DuckDB connection with the title_basics table built.

    .. returns:
        None
    """
    output_path = os.path.join(IMDB_DIR, "titles.basics.csv")
    con.execute(f"""
        COPY title_basics
        TO '{output_path}'
        (FORMAT csv, HEADER true)
        """)
    print(f"Exported title_basics to {output_path}.")


def export_ratings(con: duckdb.DuckDBPyConnection) -> None:
    """
    Export the filtered ratings table to title.ratings.csv.

    .. args:
        con: A DuckDB connection with the title_ratings table built.

    .. returns:
        None
    """
    output_path = os.path.join(IMDB_DIR, "title.ratings.csv")
    con.execute(f"""
        COPY title_ratings
        TO '{output_path}'
        (FORMAT csv, HEADER true)
        """)
    print(f"Exported title_ratings to {output_path}.")


def build_titles_table(con: duckdb.DuckDBPyConnection, filename: Path) -> None:
    """
    Create the filtered titles table.

    .. args:
        con: A DuckDB connection.
        filename: The path to the title.basics.tsv.gz file.

    .. returns:
        None
    """
    print(f"Building title_basics table from {filename}...")
    title_types = ", ".join(f"'{t}'" for t in IMDB_TITLE_TYPES)
    con.execute(
        f"""
        CREATE OR REPLACE TABLE title_basics AS
        SELECT  *,
                LOWER(REGEXP_REPLACE(primaryTitle, '[^a-z0-9 ]', '', 'g')) AS title_key
        FROM    read_csv_auto(?, delim='\t')
        WHERE   titleType IN ({title_types}) AND
                isAdult = '0'
        """,
        [str(filename)],
    )
    print("built title_basics table.")


def build_ratings_table(con: duckdb.DuckDBPyConnection, filename: Path) -> None:
    """
    Create the filtered ratings table corresponding to titles.

    .. args:
        con: A DuckDB connection.
        filename: The path to the title.ratings.tsv.gz file.

    .. returns:
        None
    """
    print(f"Building title_ratings table from {filename}...")
    con.execute(
        """
        CREATE OR REPLACE TABLE title_ratings AS
        SELECT  r.*
        FROM    read_csv_auto(?, delim='\t') AS r
                SEMI JOIN title_basics USING (tconst)
        WHERE r.numVotes >= 50
        """,
        [str(filename)],
    )
    print("built title_ratings table.")


def fetch_title_basics(with_cleanup: bool = False) -> None:
    """
    Download, build, and export the title.basics table.

    .. args:
        with_cleanup: Whether to remove the downloaded file after processing.

    .. returns:
        None
    """
    titles_url = f"{BASE_URL}/title.basics.tsv.gz"
    titles_file: Path | None

    titles_file = fetch_url(titles_url, output_dir=IMDB_DIR)

    if titles_file is None:
        raise RuntimeError("Failed to download title.basics.tsv.gz")

    try:
        with duckdb.connect(DB_FILE) as con:
            build_titles_table(con, titles_file)
            export_titles(con)

    finally:
        if with_cleanup:
            cleanup(titles_file)

    print("Generated titles.basics.csv")
    print("-" * 40)


def fetch_title_ratings(with_cleanup: bool = False) -> None:
    """
    Download, build, and export the title.ratings table.

    .. args:
        with_cleanup: Whether to remove the downloaded file after processing.

    .. returns:
        None
    """
    ratings_url = f"{BASE_URL}/title.ratings.tsv.gz"
    ratings_file: Path | None

    ratings_file = fetch_url(ratings_url, output_dir=IMDB_DIR)

    if ratings_file is None:
        raise RuntimeError("Failed to download title.ratings.tsv.gz")

    try:
        with duckdb.connect(DB_FILE) as con:
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
