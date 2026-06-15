# Python Requirements

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/PyPI-website-blue?logo=pypi)](https://pypi.org/)

Python requirements files are managed here. These files are formatted for use with the
`pip` (Python Install Package) software utility during the Docker build procedure.
The packages themselves are distributed from [pypi](https://pypi.org/). You can review
salient details for any package by searching for it on the pypi.org web site. Each package
also has its own unique url. For example, you can review the Django pypi package at
[https://pypi.org/project/Django/](https://pypi.org/project/Django/)

**DO NOT EDIT THESE FILES.**

Python requirements for this project are maintained automatically via GitHub's Dependabot service,
combined with automated ci-cd procedures that occasionally re-generate these .txt files
from the .in files located in the .in subfolder. Further instructions are included the header docs
of each .in file.

## Manually updating requirements files

You can manually run pip-compile from the root of this project, as follows:

```console
pip-compile requirements/in/local.in -o requirements/local.txt
```
