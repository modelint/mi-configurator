# MI Configurator

A configuration management service for [Model Integration](https://modelint.com) applications. It loads YAML configuration files into typed Python `NamedTuple` instances (or plain dictionaries), with automatic fallback to bundled defaults when a user's local copy is missing.

---

## Purpose

Model Integration applications typically ship a set of YAML configuration files alongside the package (colors, line styles, layout parameters, etc.). End users may customise these files locally without touching the installed package. `mi-configurator` handles:

- **Discovery** — looks for config files in `~/.config/<app_name>/`
- **Fallback** — if a file is absent from the user directory, copies the packaged default from the app's own library directory and loads it
- **Typed loading** — maps each YAML file's records to a caller-supplied `NamedTuple` type, giving attribute access instead of raw dictionary keys
- **Plain-dict loading** — when no `NamedTuple` type is supplied, returns the raw YAML data as a dictionary

---

## Requirements

- Python 3.12 or later
- PyYAML

---

## Installation

Create or activate a Python 3.12+ virtual environment, then:

```
pip install mi-configurator
```

---

## Usage

### 1. Define NamedTuples for your config records

Each YAML file that contains keyed records can be mapped to a `NamedTuple` whose fields match the keys of each record's value block.

```python
from typing import NamedTuple

class ColorCanvas(NamedTuple):
    r: int
    g: int
    b: int

class LineStyle(NamedTuple):
    pattern: str
    width: int
    color: str
```

### 2. Build the file specification

`fspec` is a dictionary that maps each config file's base name (without extension) to its `NamedTuple` type, or to `None` for a plain dictionary load.

```python
fspec = {
    'colors':      ColorCanvas,   # loaded as {name: ColorCanvas(...), ...}
    'line_styles': LineStyle,     # loaded as {name: LineStyle(...), ...}
    'settings':    None,          # loaded as a plain dict
}
```

### 3. Instantiate Config

```python
from pathlib import Path
from mi_config.config import Config

# Path to the bundled default config files inside your package
lib_config_dir = Path(__file__).parent / 'configuration'

cfg = Config(
    app_name='my_app',
    lib_config_dir=lib_config_dir,
    fspec=fspec,
)
```

On construction, `Config` immediately loads all files listed in `fspec`. The results are stored in `cfg.loaded_data`, a dictionary keyed by file base name:

```python
background = cfg.loaded_data['colors']['background']  # ColorCanvas(r=255, g=255, b=255)
thin_solid  = cfg.loaded_data['line_styles']['thin']   # LineStyle(pattern='solid', width=1, color='black')
```

### 4. Initialise the user config directory (first run)

Call this once at application startup if the user config directory may not exist yet. It creates `~/.config/<app_name>/` and copies any missing config files from `lib_config_dir`.

```python
cfg.init_user_config_dir()
```

Files that already exist in the user directory are left untouched, so user customisations are preserved.

---

## Configuration file locations

| Location | Purpose |
|---|---|
| `~/.config/<app_name>/` | User's local copies; customise these |
| `<package>/configuration/` | Packaged defaults; used as fallback |

The extension for all config files defaults to `.yaml`. A different extension can be supplied via the `ext` parameter to `Config`.

---

## API reference

### `Config(app_name, lib_config_dir, fspec, ext='yaml')`

| Parameter | Type | Description |
|---|---|---|
| `app_name` | `str` | Name of the client application; used as the subdirectory name under `~/.config/` |
| `lib_config_dir` | `Path` | Path to the directory inside the installed package that holds the default config files |
| `fspec` | `dict[str, NamedTuple \| None]` | Maps each config file base name to a `NamedTuple` type, or `None` for a plain dict |
| `ext` | `str` | File extension (without leading dot) for all config files; default `"yaml"` |

#### Attributes

- `loaded_data` — `dict[str, dict]`: all loaded configuration data, keyed by file base name

#### Methods

- `init_user_config_dir()` — creates the user config directory and copies any missing default files into it

---

## Expected YAML structure

Each YAML file should contain a mapping of named records, where each record's value is itself a mapping whose keys match the fields of the associated `NamedTuple`:

```yaml
# colors.yaml
background:
  r: 255
  g: 255
  b: 255
foreground:
  r: 0
  g: 0
  b: 0
```

If `None` is given as the type in `fspec`, the file is loaded as-is and returned as a plain Python dictionary.

---

## License

MIT — see `LICENSE` for details.

## Author

Leon Starr — [Model Integration](https://modelint.com)

Repository: https://github.com/modelint/mi_configurator
