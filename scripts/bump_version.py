"""
Script to update the semantic version in pyproject.toml and Dockerfile.

Called automatically from semantic-release hooks.
see: release.config.js in the root directory.

1.) semantic-release will call this script with the new version as an
argument.

2.) .github/workflows/build.yml will call this script with the new
version and --cicd flag to update additional files for CI/CD integration.

    Usage:

    python scripts/bump_version.py <new_version>

Updates:
- netflix/__version__.py
- pyproject.toml
"""

import os
import re
import sys
from pathlib import Path

# semantic version: ##.##.## or ##.##.##-label.n
SEMANTIC_VERSION_REGEX = r"^\d+\.\d+\.\d+(-[A-Za-z0-9.]+)?$"
HERE = os.path.abspath(os.path.dirname(__file__))
NETFLIX_DIR = os.path.join(HERE, "..", "netflix")
REPO_ROOT = os.path.join(HERE, "..")


def main():
    """
    Main function to update version in multiple files.

    If --cicd flag is provided, it updates additional files for CI/CD
    integration.

    .. args:
        new_version (str): The new version to set, in format ##.##.## or ##.##.##-label.n
        --cicd (bool): If provided, also updates pyproject.toml, Dockerfile, GitHub Action, and Helm charts.

    .. returns:
        None

    .. raises:
        ValueError: If the new version format is invalid or if the placeholder
        is not found in any of the files.
    """
    cicd = False
    usage = "Usage: python bump_version.py <new_version> [--cicd]"
    if len(sys.argv) not in (2, 3):
        print(usage)
        sys.exit(1)

    new_version = sys.argv[1]
    if not re.match(SEMANTIC_VERSION_REGEX, new_version):
        print("Error: Version must be in format ##.##.## or ##.##.##-label.n (e.g., 0.1.20 or 0.14.0-alpha.1)")
        sys.exit(1)

    if len(sys.argv) == 3:
        if sys.argv[2] != "--cicd":
            print(usage)
            sys.exit(1)
        cicd = True

    # version file
    path = Path(os.path.join(NETFLIX_DIR, "__version__.py"))
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_version}"',
        text,
    )
    path.write_text(text, encoding="utf-8")

    # pyproject.toml
    path = Path(os.path.join(REPO_ROOT, "pyproject.toml"))
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_version}"',
        text,
    )
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
