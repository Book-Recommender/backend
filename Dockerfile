FROM python:3.13.1-slim-bullseye@sha256:f6848854ba33a8ea0f93999b187aec829774d975b266a5535e84c851a8a44514 AS builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable
COPY src/ src/
RUN pdm install --prod --no-lock --no-editable

FROM python:3.13.1-slim-bullseye@sha256:f6848854ba33a8ea0f93999b187aec829774d975b266a5535e84c851a8a44514 AS prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app
COPY --from=builder /app/__pypackages__/3.12/lib pkgs/

COPY alembic/ alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./
COPY src/ src/

CMD ["./entrypoint.sh"]

EXPOSE 8000
