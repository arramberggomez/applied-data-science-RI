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
test_dir := "tests"

# -----------------------------------------------------------------
# Recipies
# -----------------------------------------------------------------

# List available Recipies
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

# Run the application
run *ARGS:
  uv run python -m applied_data_science_ri {{ARGS}}
