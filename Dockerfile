FROM python:3.10

WORKDIR /app
COPY --from=contentsquareplatform/chproxy:v1.26.4 /chproxy /usr/bin/chproxy

RUN pip3 install --no-cache-dir poetry
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry install --no-root --without dev \
    && rm -rf /root/.cache/*

COPY guesthouse guesthouse
CMD [".venv/bin/uvicorn", "guesthouse.app:app"]
