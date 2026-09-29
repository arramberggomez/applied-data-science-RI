# applied-data-science-RI
## Setup
### Requirements
- [uv](https://docs.astral.sh/uv/) (manages Python and dependencies)
- [just](https://just.systems/) (command runner)

You don't need to install Python yourself. `uv` downloads the correct version automatically.
### Quick start
#### Linux (Arch)
`sudo pacman -S uv`

`sudo pacman -S just`

#### Windows
`winget install --id astral-sh.uv -e`

`winget install --id Casey.Just -e`

#### macOS
`brew install uv`

`brew install just`


Then install the project dependencies and initialize the virtual environment by running:
```sh
just setup
```

## Usage

| Command | Description |
|---------|-------------|
| `just` | List all available commands |
| `just setup` | Install/update dependencies |
| `just run` | Run the project |
| `just add <library>` | Add a library to the environment |
