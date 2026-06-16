# Netflix Writer

[![License: GNU AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.13-blue?logo=pydantic)](https://docs.pydantic.dev/)
<br>
[![hack.d Lawrence McDaniel](https://img.shields.io/badge/Author-Lawrence%20McDaniel-orange.svg)](https://lawrencemcdaniel.com)

This repo contains source code for ...
Netflix AI Greenlight Challenge: Can Data Science Predict the Next Hit Drama?

## Quickstart

1. Register for Kaggle and get a [Kaggle API Key](./docs/KAGGLE.md)
2. Install required system packages for your operating system: [Windows](./setup/windows/setup.ps1),
   [macOS](./setup/macos/setup.sh), [Linux](./setup/linux/setup.sh)

3. Initialize your environment. This includes creating and activating a Python virtual
   environment, and then downloading data files for Netflix, IMDb and The Movie
   Database (TMDB). The final dataset will be located at `./netflix/db/netflix_enriched_dataset.csv`.

   **The setup process will take between 5 and 15 minutes depending on your compute
   device and your Internet connection.**

   ```console
   make python-init
   make run
   ```

4. Other helpful commands:

   ```console
   source venv/bin/activate
   which python3
   which pip3
   python --version # you should see Python 3.13.x
   pip --version # you should see pip 25.3.x
   ```

## Completely Remove This Project

```console
make tear-down
deactivate
```

## Support

Please report bugs to the [GitHub Issues Page](https://github.com/netflix-writers/netflix/issues)
for this project.
