"""
Download and prune Kaggle TMDB datasets.

This script downloads Kaggle TMDB's movie metadata dataset, filters it to retain only relevant information,
and exports the results to CSV files.

https://www.kaggle.com/datasets/asaniczka/full-tmdb-tv-shows-dataset-2023-150k-shows
"""

import logging
import os

from kaggle.api.kaggle_api_extended import KaggleApi  # type: ignore[import-untyped]

from netflix.const import DATA_DIR

KAGGLE_DIR = os.path.join(DATA_DIR)
DATASET = "asaniczka/full-tmdb-tv-shows-dataset-2023-150k-shows"
INPUT_FILE = "TMDB_tv_dataset_v3.csv"
OUTPUT_FILE = "tmdb.titles.v3.csv"

api = KaggleApi()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """
    Download and unzip the Kaggle TMDB movie metadata dataset.

    This function authenticates with the Kaggle API, downloads the specified dataset,
    and unzips it to the designated directory.

    Raises:
        Exception: If there is an error during authentication or dataset download.
    """
    api.authenticate()
    api.dataset_download_files(DATASET, path=KAGGLE_DIR, unzip=True)

    input_path = os.path.join(KAGGLE_DIR, INPUT_FILE)
    output_path = os.path.join(KAGGLE_DIR, OUTPUT_FILE)
    if os.path.exists(input_path):
        logger.info("Dataset downloaded successfully.")
        os.rename(input_path, output_path)
        logger.info("Renamed %s → %s", INPUT_FILE, OUTPUT_FILE)
    else:
        logger.warning("Expected file not found: %s", INPUT_FILE)
    logger.info("-" * 40)


if __name__ == "__main__":

    main()
