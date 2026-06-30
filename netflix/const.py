"""Constants for the fetch module."""

import os

HERE = os.path.abspath(os.path.dirname(__file__))
NETFLIX_DIR = os.path.join(HERE)
REPO_ROOT = os.path.join(NETFLIX_DIR, "..")

DATA_DIR = os.path.join(NETFLIX_DIR, "data")
DUCKDB_DATA_FILE = os.path.join(DATA_DIR, "imdb.duckdb")
