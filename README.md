# Netflix Writer

[![License: GNU AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.13-blue?logo=pydantic)](https://docs.pydantic.dev/)
[![pandas](https://img.shields.io/badge/pandas-2.x-blue?logo=pandas)](https://pypi.org/project/pandas/)
[![NumPy](https://img.shields.io/badge/NumPy-2.x-blue?logo=numpy)](https://pypi.org/project/numpy/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-3.x-blue)](https://pypi.org/project/matplotlib/)
[![Seaborn](https://img.shields.io/badge/Seaborn-0.13-blue)](https://pypi.org/project/seaborn/)
[![SciPy](https://img.shields.io/badge/SciPy-1.x-blue?logo=scipy)](https://pypi.org/project/scipy/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-blue?logo=scikitlearn)](https://pypi.org/project/scikit-learn/)
[![SHAP](https://img.shields.io/badge/SHAP-0.49-blue)](https://pypi.org/project/shap/)
[![RapidFuzz](https://img.shields.io/badge/RapidFuzz-3.x-blue)](https://pypi.org/project/rapidfuzz/)
<br>
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/Author-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

This repo contains source code for ...
Netflix AI Greenlight Challenge: Can Data Science Predict the Next Hit Drama?

## Quickstart

1. Register for Kaggle and get a [Kaggle API Key](./docs/KAGGLE.md)
2. Install [Anaconda](https://www.anaconda.com/download)
3. Install required system packages for your operating system: [Windows](./setup/windows/setup.ps1),
   [macOS](./setup/macos/setup.sh), [Linux](./setup/linux/setup.sh)

4. Initialize your environment by running the make commands below.
   These will create and activate a Python virtual
   environment, and then download data files for Netflix, IMDb and The Movie
   Database (TMDB).

   **The setup process will take between 5 and 15 minutes depending on your compute
   device and your Internet connection.**

   ```console
   make python-init
   make run
   ```

Creates three csv files in the ./data directory:

- imdb.titles.composite.csv
- netflix.titles.composite.csv
- TMDB_tv_dataset_v3.csv

## Data Sources

### Netflix REST API

Every Tuesday, Netflix publishes four [global Top 10 lists](https://www.kaggle.com/datasets/dhruvildave/netflix-top-10-tv-shows-and-films)
for films and TV: Film (English), TV (English), Film (Non-English), and TV (Non-English).
These lists rank titles based on weekly hours viewed: the total number of hours
that members around the world watched each title from Monday to Sunday of the
previous week.

Each season of a series and each film is considered on their own, so you might
see both Stranger Things seasons 2 and 3 in the Top 10. Because titles sometimes
move in and out of the Top 10, there is also the total number of weeks that a
season of a series or film has spent on the list.

Netflix also publishes Top 10 lists for nearly 100 countries and territories
(the same locations where there are Top 10 rows on Netflix). Country lists are
also ranked based on hours viewed but don’t show country-level viewing directly.

Finally, Netflix provides a list of the Top 10 most popular Netflix films and
TV (branded Netflix in any country) in each of the four categories based on the
hours that each title was viewed during its first 28 days.

### IMDb Non-Commercial Datasets

Subsets of [IMDb data](https://datasets.imdbws.com/title.basics.tsv.gz)
are available for access to users for personal and
non-commercial use. You can hold local copies of this data, and it is subject
to our terms and conditions. Please refer to the Non-Commercial Licensing
and copyright/license and verify compliance.

### The Movie Database

The [TMDB (The Movie Database)](https://www.kaggle.com/datasets/asaniczka/full-tmdb-tv-shows-dataset-2023-150k-shows)
is a widely-used resource for movie and TV show
data, providing valuable information such as ratings, plot summaries, and more.
This dataset contains a collection of 150,000 tv shows from the TMDB database,
collected and cleaned.

### Polti's Thirty-Six Dramatic Situations

The [Thirty-Six Dramatic Situations](https://en.wikipedia.org/wiki/The_Thirty-Six_Dramatic_Situations)
is a descriptive list which was first
proposed by Georges Polti in 1895 to categorize every dramatic situation that
might occur in a story or performance.[1] Polti analyzed classical Greek texts,
plus classical and contemporaneous French works. He also analyzed a handful of
non-French authors. In his introduction, Polti claims to be continuing the work
of Carlo Gozzi (1720–1806), who also identified 36 situations.

## Completely Remove This Project

```console
make tear-down
deactivate
```

## Helpful Commands

```console
source venv/bin/activate
which python3
which pip3
python --version # you should see Python 3.13.x
pip --version # you should see pip 25.3.x
```

## Support

Please report bugs to the [GitHub Issues Page](https://github.com/netflix-writers/netflix/issues)
for this project.
