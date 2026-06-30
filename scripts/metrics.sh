#!/usr/bin/env bash
set -euo pipefail

ruff check .
pylint app
radon cc app -s -a
radon mi app -s

