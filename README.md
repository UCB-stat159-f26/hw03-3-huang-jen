# HW3) Python Package for Tennis Abstract Data [Stat159]

## Overview
This repository contains a Python package for retrieving Tennis Abstract career match data for a given player, and plotting the player's age against the age difference with their opponent color-coded by results.

It has an `src/` source directory and a `tests/` directory, and `LICENSE`, `pyproject.toml`, and `.gitignore` files. The package code is in `src/tennis_career/`, and offline tests and sample data are in `tests/`.

## Repository structure

```text
hw03-3-huang-jen/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── src/
│   └── tennis_career/
│       ├── __init__.py
│       ├── data.py
│       └── plot.py
├── tests/
│   ├── conftest.py
│   ├── test_data.py
│   ├── test_plot.py
│   └── fixtures/
│       ├── FemalePlayerCareer.js
│       └── MalePlayerCareer.js
└── outputs/
    ├── serena_career.csv
    ├── serena_career.png
    ├── rafael_nadal_career.csv
    └── rafael_nadal_career.png
```

Local environments and caches are included. Example generated output plots and cleaned CSVs are included for reference.

## Development setup

This project requires Python 3.10 or newer.

To install the package, run from the repository root:

```bash
python -m pip install -e .
```

To also install the testing dependencies:

```bash
python -m pip install -e '.[test]'
```

Run installation and testing commands in a terminal. Run the Python examples in a notebook, Python session, or script.

## Retrieve career data

```python
from tennis_career import get_career_data

serena = get_career_data("serena williams")
print(serena.head())

rafa = get_career_data("Rafael Nadal")
print(rafa.head())
```

The function accepts spaced names such as `"serena williams"` and `"Serena Williams"`, or joined names such as `"SerenaWilliams"`. For unusual names, use the TA site's exact joined spelling and capitalization. Use unaccented names and be sure to add a space for lowercase names, as fully lowercase joined names are not supported. The function returns a pandas DataFrame containing match details, player and opponent ages, and their age difference. A positive difference means the player is older than the opponent.

Using TA, female historical JS files provide opponents’ birth dates, while male historical JS files provide opponents’ ages directly. The package checks each value’s format, converting birth dates into ages and retaining numeric ages. This also accommodates current files that use birth dates. Calculated ages use days divided by 365.25.

Matches with missing or invalid dates or ages, ages outside 0–100, or results other than W/L are excluded. Duplicate cleaned matches are removed. Qualifying and lower-level events are kept if present, and source dates may represent tournament dates rather than exact match days.

Retrieval first checks the player profile, falling back to the regular JS file if the profile does not match. Historical matches are added when indicated by the source. This helps include recent matches missing from some JS files. Retrieval requires internet access. Invalid players or unusable data raise `ValueError`. Connection failures and server errors raise `ConnectionError`.

## Plot career

```python
import matplotlib.pyplot as plt
from tennis_career import plot_career

ax = plot_career(serena)
plt.show()
```

The horizontal axis shows player age, and the vertical axis shows player age minus opponent age. Wins are blue and losses are purple.

`plot_career()` returns a Matplotlib Axes without changing the input data. It checks for empty data and expects the cleaned DataFrame from `get_career_data()`.

Displaying and saving are optional function call actions, not automatically executed inside the function. If you would like to save the cleaned data as a CSV and the plot as a PNG instead of displaying it:

```python
from pathlib import Path

Path("outputs").mkdir(exist_ok=True)
serena.to_csv("outputs/serena_career.csv", index=False)

ax = plot_career(serena)
ax.figure.savefig("outputs/serena_career.png", dpi=300)
plt.close(ax.figure)
```

`plt.close(ax.figure)` releases the figure after saving.

## Tests

Run all tests from the repository root:

```bash
python -m pytest
```

The tests use the instructions' female and male mockup JS data and small plotting examples. Automated tests do not contact live servers.

## Install from GitHub

```bash
python -m pip install git+https://github.com/UCB-stat159-f26/hw03-3-huang-jen.git
```

## License

The package code is released under the terms of the BSD 3-Clause License.