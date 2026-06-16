"""Unified dataset builder for Netflix + TMDB + IMDb."""

import logging
import re
from pathlib import Path
from typing import Optional

import duckdb
import pandas as pd
from rapidfuzz.distance import JaroWinkler
from tqdm import tqdm

from .const import DB_DIR, DB_FILE

KAGGLE_PATH = Path(DB_DIR) / "kaggle"
IMDB_PATH = Path(DB_DIR) / "imdb"

IMDB_TITLES_BASICS_FILE = IMDB_PATH / "title.basics.tsv.gz"
IMDB_TITLE_RATINGS_FILE = IMDB_PATH / "title.ratings.tsv.gz"

TMDB_TV_DATA_FILE = KAGGLE_PATH / "tmdb-movie-metadata" / "TMDB_tv_dataset_v3.csv"
NETFLIX_FILE = KAGGLE_PATH / "netflix-top-10-tv-shows-and-films" / "all-weeks-global.csv"

NETFLIX_ENRICHED_DATASET_FILE = Path(DB_DIR) / "netflix_enriched_dataset.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def fuzzy_match(
    base: pd.DataFrame,
    source: pd.DataFrame,
    columns: list[str] | None = None,
    score_threshold: float = 0.85,
    source_name: str = "source",
) -> pd.DataFrame:
    """
    Performs fuzzy matching between the base and source datasets.

    .. args::
        base: pd.DataFrame The base DataFrame to match against.
        source: pd.DataFrame The source DataFrame to match.
        score_threshold: float The minimum similarity score to consider a match.
        source_name: str The name of the source dataset (for logging purposes).

    .. returns::
        A pd.DataFrame containing the matched titles.
    """
    logger.info("Fuzzy matching %s to Netflix with score threshold %s...", source_name, score_threshold)
    candidates = base.merge(source, on="key", how="inner")
    logger.info("Found %d candidate pairs after blocking on key.", len(candidates))

    if candidates.empty:
        return pd.DataFrame(columns=["netflix_title", f"{source_name}_title"])

    # year filter
    if "year" in candidates.columns:
        candidates = candidates[candidates["year"].isna() | (candidates["year_hint"] >= (candidates["year"] - 1))]
        logger.info("%d candidates remain after year filtering.", len(candidates))

    if candidates.empty:
        return pd.DataFrame(columns=["netflix_title", f"{source_name}_title"])

    candidates["score"] = candidates.apply(
        lambda r: JaroWinkler.normalized_similarity(r["clean_title"], r["clean_netflix_title"]),
        axis=1,
    )

    candidates = candidates[candidates["score"] >= score_threshold]

    best = candidates.sort_values(["score"], ascending=False).drop_duplicates(subset=["netflix_title"], keep="first")

    logger.info("Matched %d out of %d Netflix titles to %s.", len(best), len(base), source_name)
    columns = columns or []
    rename_map = {col: f"{source_name}_{col}" for col in columns if col != "netflix_title"}
    selected = ["netflix_title", *columns]
    return best[selected].rename(columns=rename_map)


def log_dataframe_info(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Logs detailed information about a DataFrame, including its shape, schema,.

    and memory usage.

    .. args::
        df: The DataFrame to log information about.
        name: A name to identify the DataFrame in the logs.

    .. returns::
        None
    """

    logger.info("=== %s DataFrame Schema Info ===", name)
    logger.info("%s shape: %s rows × %s columns", name, *df.shape)
    logger.info("%s schema:", name)

    for col in df.columns:
        logger.info(
            "  %-30s %-15s nulls=%-8d unique=%-8d",
            col,
            str(df[col].dtype),
            int(df[col].isna().sum()),
            int(df[col].nunique(dropna=True)),
        )

    memory_mb = df.memory_usage(deep=True).sum() / (1024**2)

    logger.info("%s memory usage: %.2f MB", name, memory_mb)
    logger.info("=== END %s DataFrame Schema Info ===\n\n", name)


def read_csv(path: Path, total_rows: Optional[int] = None, chunksize: int = 10_000, **kwargs) -> pd.DataFrame:
    """
    Reads a CSV file in chunks and concatenates them into a single DataFrame,.

    while displaying a progress bar.

    .. args::
        path: The path to the CSV file.
        total_rows: The total number of rows in the CSV file (optional).
        chunksize: The number of rows per chunk (default: 10,000).
        **kwargs: Additional keyword arguments to pass to pd.read_csv.

    .. returns::
        A concatenated DataFrame containing all the data from the CSV file.
    """
    chunks = []
    reader = pd.read_csv(path, chunksize=chunksize, **kwargs)

    if total_rows is None:
        pbar = tqdm(desc=path.name, unit="chunks")
    else:
        pbar = tqdm(
            total=total_rows,
            desc=path.name,
            unit="rows",
            unit_scale=True,
        )

    with pbar:
        for chunk in reader:
            chunks.append(chunk)

            if total_rows is None:
                pbar.update(1)
            else:
                pbar.update(len(chunk))

    return pd.concat(chunks, ignore_index=True)


def _clean(s: str) -> str:
    """
    Cleans a string by converting it to lowercase, removing certain words,.

    and replacing non-alphanumeric characters with spaces.

    .. args::
        s: str The string to clean.

    .. returns::
        str The cleaned string.
    """
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""

    s = str(s).lower()
    s = re.sub(r"\band\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def get_blocking_key(title: str) -> str:
    """
    Generates a blocking key for a given title by cleaning the title,.

    removing stop words, and taking the first two characters of the
    first three tokens.

    .. args::
        title: str The title to generate a blocking key for.

    .. returns::
        str A blocking key string.
    """
    cleaned = _clean(title)
    if not cleaned:
        return "empty"

    stop_words = {"the", "a", "an", "of", "in", "to", "for", "with", "on", "at"}
    tokens = [t for t in cleaned.split() if t not in stop_words] or cleaned.split()

    parts = sorted([t[:2] for t in tokens[:3]])
    return "_".join(parts) if parts else "empty"


# =========================================================
# LOAD
# =========================================================
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads the Netflix, TMDB, and IMDb datasets.

    .. returns::
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        A tuple containing the loaded DataFrames: (netflix_pd, tmdb_pd,
        imdb_basics_pd, imdb_ratings_pd)
    """
    netflix_pd = read_csv(NETFLIX_FILE)
    tmdb_pd = read_csv(TMDB_TV_DATA_FILE)
    imdb_basics_pd = read_csv(IMDB_TITLES_BASICS_FILE, sep="\t", low_memory=False)
    imdb_ratings_pd = read_csv(IMDB_TITLE_RATINGS_FILE, sep="\t", low_memory=False)

    return (netflix_pd, tmdb_pd, imdb_basics_pd, imdb_ratings_pd)


# =========================================================
# NETFLIX
# =========================================================
def build_netflix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the Netflix dataset by cleaning titles, generating blocking keys,.

    and aggregating viewing data.

    .. args::
        df: pd.DataFrame The Netflix DataFrame to preprocess.

    .. returns::
        A preprocessed Netflix DataFrame.
    """
    logger.info("Building Pandas DataFrame for Netflix data...")
    df = df.copy()

    df["week_date"] = pd.to_datetime(df["week"], errors="coerce")
    df["year_hint"] = df["week_date"].dt.year

    df["key"] = df["show_title"].apply(get_blocking_key)
    df["clean_title"] = df["show_title"].apply(_clean)

    retval = df.groupby("key", as_index=False).agg(
        viewing_hours=("weekly_hours_viewed", "sum"),
        weeks=("cumulative_weeks_in_top_10", "max"),
        year_hint=("year_hint", "min"),
        netflix_title=("show_title", "first"),
        clean_netflix_title=("clean_title", "first"),
    )
    log_dataframe_info(retval, "Netflix")
    return retval


# =========================================================
# TMDB
# =========================================================
def build_tmdb(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the TMDB dataset by cleaning titles, generating blocking keys,.

    and extracting relevant information.

    .. args::
        df: pd.DataFrame The TMDB DataFrame to preprocess.

    .. returns::
        A preprocessed TMDB DataFrame.
    """
    logger.info("Building Pandas DataFrame for TMDB data...")
    tmdb = df.copy()

    tmdb["title"] = tmdb.get("name", tmdb.get("original_name", ""))

    first_air_date = tmdb.get("first_air_date")
    if first_air_date is not None:
        tmdb["year"] = pd.to_datetime(
            first_air_date,
            errors="coerce",
        ).dt.year
    else:
        tmdb["year"] = pd.NA

    tmdb["clean_title"] = tmdb["title"].apply(_clean)
    tmdb["key"] = tmdb["title"].apply(get_blocking_key)

    retval = tmdb[
        [
            "key",
            "title",
            "clean_title",
            "year",
            "popularity",
            "vote_average",
            "vote_count",
        ]
    ]
    log_dataframe_info(retval, "TMDB")
    return retval


# =========================================================
# IMDB
# =========================================================
def build_imdb(basics: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocesses the IMDb dataset by joining basics and ratings,.

    cleaning titles, and generating blocking keys.

    .. args::
        basics: pd.DataFrame The IMDb basics DataFrame.
        ratings: pd.DataFrame The IMDb ratings DataFrame.

    .. returns::
        A preprocessed IMDb DataFrame.
    """
    logger.info("Building Pandas DataFrame for IMDb data...")

    con = duckdb.connect(DB_FILE)
    con.register("basics", basics)
    con.register("ratings", ratings)

    query = """
        SELECT
            b.tconst,
            b.primaryTitle AS title,
            CASE
                WHEN b.startYear = '\\N' THEN NULL
                ELSE CAST(b.startYear AS INTEGER)
            END AS year,
            r.averageRating,
            r.numVotes
        FROM basics b
        LEFT JOIN ratings r
            ON b.tconst = r.tconst
    """

    df = con.execute(query).df()
    logger.info("Joined IMDb basics and ratings: %d records.", len(df))
    con.close()

    logger.info("Cleaning IMDb titles...")
    df["clean_title"] = df["title"].apply(_clean)

    logger.info("Generating blocking keys for IMDb titles...")
    df["key"] = df["title"].apply(get_blocking_key)
    log_dataframe_info(df, "IMDb")
    logger.info("Final IMDb dataset has %d records.", len(df))
    return df


# =========================================================
# Netflix Enriched Dataset
# =========================================================
def create_dataset() -> pd.DataFrame:
    """
    Creates a unified dataset by loading, preprocessing, and fuzzy matching.

    TMDB and IMDb datasets to Netflix.

    .. returns::
        A pd.DataFrame containing matched titles from all sources.
    """
    netflix_raw, tmdb_raw, imdb_basics, imdb_ratings = load_data()

    netflix = build_netflix(netflix_raw)
    tmdb = build_tmdb(tmdb_raw)
    imdb = build_imdb(imdb_basics, imdb_ratings)

    # LEFT JOIN SOURCES
    tmdb_map = fuzzy_match(
        netflix,
        tmdb,
        source_name="tmdb",
        columns=[
            "title",
            "popularity",
            "vote_average",
            "vote_count",
        ],
    )
    imdb_map = fuzzy_match(
        netflix,
        imdb,
        source_name="imdb",
        columns=[
            "title",
            "averageRating",
            "numVotes",
        ],
    )

    result = netflix.merge(tmdb_map, on="netflix_title", how="left")
    result = result.merge(imdb_map, on="netflix_title", how="left")

    log_dataframe_info(result, "Final dataset")
    logger.info("Dataset head:\n%s", result.head())

    result.to_csv(NETFLIX_ENRICHED_DATASET_FILE, index=False)
    return result


def main():
    create_dataset()


if __name__ == "__main__":
    main()
