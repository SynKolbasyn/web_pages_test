FROM debian:stable-slim

RUN apt update
RUN apt upgrade -y
RUN apt install -y curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_PREFERENCE=only-managed
ENV PYTHONUNBUFFERED=1

WORKDIR /app/


COPY ./.python-version ./
RUN $HOME/.local/bin/uv python install

COPY ./pyproject.toml ./
RUN $HOME/.local/bin/uv sync --no-dev

COPY ./src/ ./src/
COPY ./alembic.ini ./
COPY ./alembic/ ./alembic/
COPY ./.env ./

CMD ["sh", "-c", "export PATH=$PATH:$HOME/.local/bin/ && uv run --no-dev alembic upgrade head && uv run --no-dev gunicorn src.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:80 -w $(nproc)"]
