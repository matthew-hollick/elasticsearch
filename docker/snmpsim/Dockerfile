FROM ghcr.io/astral-sh/uv:debian-slim

RUN addgroup snmpsim && useradd snmpsim -g snmpsim

RUN mkdir /app && chown snmpsim:snmpsim /app

USER snmpsim

WORKDIR /app

COPY docker-pyproject.toml /app/pyproject.toml

COPY docker-python-version /app/.python-version

ENV UV_NO_CACHE=true
ENV UV_DIRECTORY=/app
ENV UV_PYTHON_INSTALL_DIR=/app/python

RUN uv python install 3.13 --install-dir /app/python
# RUN uv python install 3.13 --directory /app --install-dir /app/python


RUN uv venv --python=3.13
# RUN uv venv --python=3.13 --directory /app

ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync

RUN cd /app && uv run setup-snmpsim-data /app/data

ENTRYPOINT uv run snmpsim-command-responder --v3-engine-id auto --data-dir=data/network/switch --agent-udpv4-endpoint=127.0.0.1:1611 --v3-engine-id auto --data-dir=data/storage --agent-udpv4-endpoint=127.0.0.1:1612

EXPOSE 1161/udp
EXPOSE 1162/udp
