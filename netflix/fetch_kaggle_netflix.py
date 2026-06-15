"""
Download and prune Kaggle Netflix datasets.

This script downloads Kaggle Netflix's top 10 TV shows and films dataset and
TMDB movie metadata dataset, filters them to retain only relevant information,
and exports the results to CSV files.

https://www.kaggle.com/datasets/dhruvildave/netflix-top-10-tv-shows-and-films
https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata
"""

import os

from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore[import-untyped]

from .const import DB_DIR

BASE_URL = "https://"
KAGGLE_DIR = os.path.join(DB_DIR, "kaggle", "netflix-top-10-tv-shows-and-films")
DATASET = "dhruvildave/netflix-top-10-tv-shows-and-films"

api = KaggleApi()


if __name__ == "__main__":

    api.authenticate()
    api.dataset_download_files(DATASET, path=KAGGLE_DIR, unzip=True)
    print("Dataset downloaded successfully.")
