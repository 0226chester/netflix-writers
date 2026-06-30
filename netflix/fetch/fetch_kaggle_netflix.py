"""
Download and prune Kaggle Netflix datasets.

This script downloads Kaggle Netflix's top 10 TV shows and films dataset and
TMDB movie metadata dataset, filters them to retain only relevant information,
and exports the results to CSV files.

https://www.kaggle.com/datasets/dhruvildave/netflix-top-10-tv-shows-and-films
"""

import logging
import os

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore[import-untyped]

from netflix.const import DATA_DIR

KAGGLE_DIR = os.path.join(DATA_DIR, "kaggle", "netflix-top-10-tv-shows-and-films")
DATASET = "dhruvildave/netflix-top-10-tv-shows-and-films"

kaggle_api = KaggleApi()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """
    Download and unzip the Kaggle Netflix top 10 TV shows and films dataset.

    This function authenticates with the Kaggle API, downloads the specified dataset,
    and unzips it to the designated directory.

    Raises:
        Exception: If there is an error during authentication or dataset download.
    """
    kaggle_api.authenticate()
    kaggle_api.dataset_download_files(DATASET, path=KAGGLE_DIR, unzip=True)
    logger.info("Dataset downloaded successfully.")
    logger.info("-" * 40)

    all_weeks_csv_path = os.path.join(KAGGLE_DIR, "all-weeks-global.csv")
    unique_shows_csv_path = os.path.join(KAGGLE_DIR, "unique-shows.csv")
    df = pd.read_csv(all_weeks_csv_path)

    unique_shows = df[["show_title"]].dropna().drop_duplicates().sort_values("show_title")

    unique_shows.to_csv(unique_shows_csv_path, index=False)
    print(f"Found {len(unique_shows)} unique shows.")


if __name__ == "__main__":

    main()
