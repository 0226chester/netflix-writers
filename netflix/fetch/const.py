"""Constants for the fetch module."""

import os

HERE = os.path.abspath(os.path.dirname(__file__))

DB_DIR = os.path.join(HERE, "db")
DB_FILE = os.path.join(DB_DIR, "imdb.duckdb")
