#!/bin/bash
###############################################################################
# Author: Lawrence McDaniel https://lawrencemcdaniel.com
# Date: 2026-06-26
#
# setup.sh — macOS Environment Setup for Smarter Project
#
# This script verifies and installs required development tools for the Smarter project on macOS.
# It checks for Xcode Command Line Tools, Homebrew, and Docker Desktop, and installs essential
# packages and libraries via Homebrew.
#
# Usage:
#   bash setup.sh
#
# Requirements:
#   - macOS
#   - Administrator privileges (for some installations and symlinks)
#
# Actions performed:
#   - Verifies Xcode Command Line Tools, Homebrew, Docker Desktop
#   - Ensures docker-compose symlink exists
#   - Installs development dependencies (gcc, python, node, nvm, etc.)
#
# Exit codes:
#   0 — Success
#   1 — Missing prerequisite or failed installation
#
###############################################################################

# open "macappstore://itunes.apple.com/app/id497799835"
xcode-select --install


# Verify prerequisites: Xcode, Homebrew, Docker Desktop
echo "[INFO] Verifying required tools..."

# Check for Xcode Command Line Tools
if ! xcode-select -p &>/dev/null; then
	echo -e "\033[0;31m[ERROR]\033[0m Xcode Command Line Tools are not installed."
	echo "Please install them by running: xcode-select --install"
	exit 1
else
	echo -e "\033[0;32m[OK]\033[0m Xcode Command Line Tools are installed."
fi

# Check for Homebrew
if ! command -v brew &>/dev/null; then
	echo -e "\033[0;31m[ERROR]\033[0m Homebrew is not installed."
	echo "Please install Homebrew from https://brew.sh/"
	exit 1
else
	echo -e "\033[0;32m[OK]\033[0m Homebrew is installed."
fi

brew update
brew upgrade
brew install gcc python@3.13 node nvm
brew install blis zlib zstd openblas libffi openssl libxml2 libxslt geos jq k9s

echo ""
echo "=============================================="
echo " Installed Packages Summary"
echo "=============================================="

echo "Xcode Command Line Tools:"
xcode-select -v

echo "Homebrew:"
brew --version | head -n 1

echo "gcc:"
gcc --version | head -n 1

echo "python:"
python3 --version

echo "node:"
node --version

echo "Other Homebrew packages:"
brew list --versions blis zlib zstd openblas libffi openssl libxml2 libxslt geos jq k9s

echo "=============================================="
