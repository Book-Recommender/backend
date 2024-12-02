# book-recommender

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

To test database functionality, if the above command does not work type:

```bash
pip install pdm
```

If that doesn't work try

```bash
pip3 install pdm
```

```bash
PYTHONPATH=src pdm test
```

To test both type:

```bash
PYTHONPATH=src pytest tests/
```

## Running

Run in dev mode with

```bash
pdm run fastapi dev src/openbook/server.py
```
