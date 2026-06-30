"""
Download and prune IMDb datasets.

Pipeline:
    1. Download IMDb TSV files
    2. Build filtered DuckDB tables
    3. Export CSVs
    4. Build composite 1-row-per-title dataset
"""

import logging
import os
from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd

from netflix.const import DATA_DIR, DUCKDB_DATA_FILE

from .lib import fetch_url

BASE_URL = "https://datasets.imdbws.com"
IMDB_DIR = os.path.join(DATA_DIR, "imdb")

IMDB_TITLE_TYPES = ["tvSeries"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def export_composite(con: duckdb.DuckDBPyConnection) -> None:
    """
    Export the composite titles table to CSV.

    Args:
        con: DuckDB connection

    Returns:
        None
    """
    output_path = os.path.join(DATA_DIR, "imdb.titles.composite.csv")

    con.execute(f"""
        COPY titles_composite
        TO '{output_path}'
        (FORMAT csv, HEADER true)
    """)

    logger.info("Exported titles_composite → %s", output_path)
    pd.read_csv(output_path).head()


def export_table(con, table: str, filename: str) -> None:
    """
    Export a DuckDB table to CSV.

    Args:
        con: DuckDB connection
        table: Name of the DuckDB table to export
        filename: Name of the CSV file to export

    Raises:
        RuntimeError: If the export fails

    Returns:
        None
    """
    output_path = os.path.join(IMDB_DIR, filename)
    con.execute(f"""
        COPY {table}
        TO '{output_path}'
        (FORMAT csv, HEADER true)
    """)
    logger.info("Exported %s → %s", table, output_path)


def build_titles_table(con, filename: Path) -> None:
    """
    Build the title_basics table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building title_basics...")

    title_types = ", ".join(f"'{t}'" for t in IMDB_TITLE_TYPES)

    con.execute(f"""
        CREATE OR REPLACE TABLE title_basics AS
        SELECT *,
            LOWER(REGEXP_REPLACE(primaryTitle, '[^a-z0-9 ]', '', 'g')) AS title_key
        FROM read_csv_auto('{filename}', delim='\t')
        WHERE titleType IN ({title_types})
          AND isAdult = '0'
    """)


def build_ratings_table(con, filename: Path) -> None:
    """
    Build the title_ratings table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building title_ratings...")

    con.execute(f"""
        CREATE OR REPLACE TABLE title_ratings AS
        SELECT r.*
        FROM read_csv_auto('{filename}', delim='\t') r
        SEMI JOIN title_basics USING (tconst)
        WHERE numVotes >= 50
    """)


def build_akas_table(con, filename: Path) -> None:
    """
    Build the title_akas table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building title_akas...")

    con.execute(f"""
        CREATE OR REPLACE TABLE title_akas AS
        SELECT a.*
        FROM read_csv_auto('{filename}', delim='\t') a
        SEMI JOIN title_basics ON a.titleId = tconst
    """)


def build_crew_table(con, filename: Path) -> None:
    """
    Build the title_crew table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building title_crew...")

    con.execute(f"""
        CREATE OR REPLACE TABLE title_crew AS
        SELECT c.*
        FROM read_csv_auto('{filename}', delim='\t') c
        SEMI JOIN title_basics USING (tconst)
    """)


def build_principals_table(con, filename: Path) -> None:
    """
    Build the title_principals table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building title_principals...")

    con.execute(f"""
        CREATE OR REPLACE TABLE title_principals AS
        SELECT p.*
        FROM read_csv_auto('{filename}', delim='\t') p
        SEMI JOIN title_basics USING (tconst)
    """)


def build_names_table(con, filename: Path) -> None:
    """
    Build the name_basics table from the IMDb TSV file.

    Args:
        con: DuckDB connection
        filename: Path to the IMDb TSV file

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building name_basics...")

    con.execute(f"""
        CREATE OR REPLACE TABLE name_basics AS
        SELECT *
        FROM read_csv_auto('{filename}', delim='\t')
    """)


def build_composite_titles_table(con) -> None:
    """
    Build a composite table of IMDb titles with the following columns:

        - tconst
        - titleType
        - primaryTitle
        - originalTitle
        - startYear
        - endYear
        - runtimeMinutes
        - genres
        - title_key
        - averageRating
        - numVotes
        - all_akas
        - cast
        - directors
        - writers

    Args:
        con: DuckDB connection

    Raises:
        RuntimeError: If the table creation fails

    Returns:
        None
    """
    logger.info("Building composite table...")

    con.execute("""
        CREATE OR REPLACE TABLE titles_composite AS

        WITH

        akas AS (
            SELECT
                titleId AS tconst,
                STRING_AGG(DISTINCT LOWER(title), ' | ') AS all_akas
            FROM title_akas
            WHERE title IS NOT NULL
            GROUP BY titleId
        ),

        principals AS (
            SELECT
                p.tconst,
                STRING_AGG(DISTINCT n.primaryName, ' | ') AS cast
            FROM title_principals p
            LEFT JOIN name_basics n USING (nconst)
            GROUP BY p.tconst
        )

        SELECT
            b.tconst,
            b.titleType,
            b.primaryTitle,
            b.originalTitle,
            b.startYear,
            b.endYear,
            b.runtimeMinutes,
            b.genres,
            b.title_key,

            r.averageRating,
            r.numVotes,

            a.all_akas,
            p.cast,

            c.directors,
            c.writers

        FROM title_basics b
        LEFT JOIN title_ratings r USING (tconst)
        LEFT JOIN akas a USING (tconst)
        LEFT JOIN principals p USING (tconst)
        LEFT JOIN title_crew c USING (tconst)
    """)


def fetch_and_build(con, url: str, builder, table_name: str, export_name: Optional[str] = None):
    """
    Fetch a URL, build a DuckDB table, and optionally export to CSV.

    Args:
        con: DuckDB connection
        url: URL to fetch
        builder: Function to build the DuckDB table
        table_name: Name of the DuckDB table to create
        export_name: Optional name of the CSV file to export

    Raises:
        RuntimeError: If the download fails

    Returns:
        Path to the downloaded file
    """
    file = fetch_url(url, output_dir=IMDB_DIR)

    if file is None:
        raise RuntimeError(f"Failed download: {url}")

    builder(con, file)

    if export_name:
        export_table(con, table_name, export_name)

    return file


def main() -> None:
    """Main function to run the IMDb pipeline."""
    logger.info("Starting IMDb pipeline...")

    with duckdb.connect(DUCKDB_DATA_FILE) as con:
        fetch_and_build(con, f"{BASE_URL}/title.basics.tsv.gz", build_titles_table, "title_basics", "titles.basics.csv")
        fetch_and_build(
            con, f"{BASE_URL}/title.ratings.tsv.gz", build_ratings_table, "title_ratings", "title.ratings.csv"
        )
        fetch_and_build(con, f"{BASE_URL}/title.akas.tsv.gz", build_akas_table, "title_akas", "title.akas.csv")
        fetch_and_build(con, f"{BASE_URL}/title.crew.tsv.gz", build_crew_table, "title_crew", "title.crew.csv")
        fetch_and_build(
            con,
            f"{BASE_URL}/title.principals.tsv.gz",
            build_principals_table,
            "title_principals",
            "title.principals.csv",
        )
        fetch_and_build(con, f"{BASE_URL}/name.basics.tsv.gz", build_names_table, "name_basics")

        build_composite_titles_table(con)
        export_composite(con)

    logger.info("IMDb pipeline complete.")


if __name__ == "__main__":
    main()
