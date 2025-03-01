FROM python:3.13.2-slim-bullseye@sha256:31b581c8218e1f3c58672481b3b7dba8e898852866b408c6a984c22832523935 AS builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable
COPY src/ src/
RUN pdm install --prod --no-lock --no-editable

FROM python:3.13.2-slim-bullseye@sha256:31b581c8218e1f3c58672481b3b7dba8e898852866b408c6a984c22832523935 AS prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app
COPY --from=builder /app/__pypackages__/3.12/lib pkgs/

COPY alembic/ alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./
COPY src/ src/

CMD ["./entrypoint.sh"]

EXPOSE 8000
