"""This module contains functions to fetch data from external APIs and save to local files."""

from .fetch_imdb import main as fetch_imdb
from .fetch_kaggle_netflix import main as fetch_kaggle_netflix
from .fetch_kaggle_tmdb import main as fetch_kaggle_tmdb
from .fetch_polti import main as fetch_polti


def main():
    fetch_imdb()
    fetch_kaggle_netflix()
    fetch_kaggle_tmdb()
    fetch_polti()


main()
