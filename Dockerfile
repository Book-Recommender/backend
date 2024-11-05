FROM python:3.13.0-slim-bullseye@sha256:5f806dfaaf027b52e0982a4aa0246acb902d8c8d12e0965015440099c63759a2 AS builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable
COPY src/ src/
RUN pdm install --prod --no-lock --no-editable

FROM python:3.13.0-slim-bullseye@sha256:5f806dfaaf027b52e0982a4aa0246acb902d8c8d12e0965015440099c63759a2 AS prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app
COPY --from=builder /app/__pypackages__/3.12/lib pkgs/

COPY src/ src/

CMD ["python", "-m", "fastapi", "run", "src/openbook/server.py"]

EXPOSE 8000
