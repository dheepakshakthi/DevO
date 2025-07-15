FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY poetry.lock . 

RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --without dev

COPY src /app/src
COPY examples /app/examples
COPY tests /app/tests

RUN python -m compileall /app/src
RUN python -m compileall /app/examples


FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app /app

RUN useradd -m -u 1000 appuser
RUN chown -R appuser:appuser /app
USER appuser

ENV FLASK_APP=/app/src/flask/__init__.py
ENV FLASK_ENV=production
ENV PORT=8080

EXPOSE $PORT

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD redis-cli ping || exit 1

CMD ["flask", "run", "--host=0.0.0.0", "--port=$PORT"]