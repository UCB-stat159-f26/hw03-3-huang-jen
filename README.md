# HW3) Python Package for Tennis Abstract Data [Stat159]

## Overview
This repository contains a Python package for retrieving Tennis Abstract career match data for a given player, and plotting the player's age against the age difference with their opponent color-coded by results.

It has an `src/` source directory and a `tests/` directory, and `LICENSE`, `pyproject.toml`, and `.gitignore` files. The package code is in `src/tennis_career/`, and offline tests and sample
data are in `tests/`.

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

## Retrieve career data

```python
from tennis_career import get_career_data

serena = get_career_data("serena williams")
print(serena.head())

rafa = get_career_data("Rafael Nadal")
print(rafa.head())
```

The function accepts spaced names such as `"serena williams"` and `"Serena Williams"` or Tennis Abstract identifiers such as `"SerenaWilliams"`. For unusual names, use the TA site's exact identifier.

It returns a pandas DataFrame containing match details, player and opponent ages, and their age difference. A positive difference means the player is older than the opponent.

Retrieval requires internet access. Invalid players or unusable data raise `ValueError`. Connection failures and server errors raise `ConnectionError`.

## Tests

Run the data tests from the repository root:

```bash
python -m pytest tests/test_data.py
```

The tests use the instructions' female and male mockup JS data. Automated tests do not contact live servers.

## License

The package code is released under the terms of the BSD 3-Clause License.