FROM python:3.12.6-slim-bullseye@sha256:6fe70237cff8ad7c0a91b992cb7cb454187dfd2e3f08ce2d023907d76db8c287 AS builder

RUN pip install -U pip setuptools wheel && pip install pdm

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable
COPY src/ src/
RUN pdm install --prod --no-lock --no-editable

FROM python:3.12.6-slim-bullseye@sha256:6fe70237cff8ad7c0a91b992cb7cb454187dfd2e3f08ce2d023907d76db8c287 AS prod

ENV PYTHONPATH=/app/pkgs
WORKDIR /app
COPY --from=builder /app/__pypackages__/3.12/lib pkgs/

COPY model.onnx model.onnx
COPY src/ src/

CMD ["python", "-m", "fastapi", "run", "src/openbook/server.py"]

EXPOSE 8000
