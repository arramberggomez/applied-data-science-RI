# Linux & macOS: bash with strict mode
set shell :=["bash", "-euo", "pipefail", "-c"]

# Windows: PowerShell
set windows-shell := ["powershell.exe", "-NoLogo", "-NoProfile", "-Command"]

# Load variables from a .env file if present
set dotenv-load := true

# No need for this because uv is great!
# # Variables (OS-dependent)
# system_python := if os() == "windows" {"python"} else {"python3"}
#
# venv := ".venv"
# venv_bin := if os() == "windows" {venv + "/Scripts"} else {venv + "bin/"}
# python := venb_bin + "/python"
#
src_dir := "src"

# -----------------------------------------------------------------
# Recipes
# -----------------------------------------------------------------

# List available recipes
default:
  @just --list

# Setup project (Create venv and install dependencies)
setup:
  uv sync

# Re-resolve and upgrade all locked dependencies
upgrade:
  uv lock --upgrade
  uv sync

# Add a dependency. `just add pandas` or `just add --dev pandas`
add *ARGS:
  uv add {{ARGS}}

# Run a pipeline step: `just run clean --nrows 100000`, `just run all`
run *ARGS:
  uv run python -m applied_data_science_ri {{ARGS}}

# Download the raw dataset from Kaggle (needs Kaggle credentials)
download:
  uv run python -m applied_data_science_ri download

# Run the whole pipeline end to end
all *ARGS:
  uv run python -m applied_data_science_ri all {{ARGS}}

# Lint and check formatting
lint:
  uv run ruff check {{src_dir}}
  uv run ruff format --check {{src_dir}}

# Auto-fix lint issues and format the code
fmt:
  uv run ruff check --fix {{src_dir}}
  uv run ruff format {{src_dir}}

# Export requirements.txt from the lockfile (alternative environment spec)
requirements:
  uv export --no-hashes --no-dev --format requirements-txt -o requirements.txt

# Build the report PDF (needs latexmk and a TeX distribution)
report:
  cd report && latexmk -pdf -interaction=nonstopmode main.tex
