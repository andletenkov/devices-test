FROM python:3.9-slim

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && \
    poetry install
COPY ./ .
CMD ["poetry", "run", "pytest", "tests/"]