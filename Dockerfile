FROM python:3.13.0-slim-bullseye@sha256:4b60efbc8e7ad07d50f9656de4108c2de55cd3a835ea75452ecab1310a178325 AS builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable
COPY src/ src/
RUN pdm install --prod --no-lock --no-editable

FROM python:3.13.0-slim-bullseye@sha256:4b60efbc8e7ad07d50f9656de4108c2de55cd3a835ea75452ecab1310a178325 AS prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app
COPY --from=builder /app/__pypackages__/3.12/lib pkgs/

COPY alembic/ alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./
COPY src/ src/

CMD ["./entrypoint.sh"]

EXPOSE 8000
