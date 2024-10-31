# book-recommender

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Book-Recommender/backend/main.svg)](https://results.pre-commit.ci/latest/github/Book-Recommender/backend/main)

## Development

We use `PDM` for packaging (see [PDM](https://pdm-project.org/latest/)). Install the project and dev dependencies with

```bash
pdm install -d
```

We use `pre-commit`. Install the hooks with

```bash
pdm run pre-commit install
```

## Tests

We use `pytest`. Run tests with

```bash
pdm test
```

## Running

Run in dev mode with

```bash
pdm run fastapi dev src/openbook/server.py
```
