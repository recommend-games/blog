################################################################################
# Shared base.
FROM ghcr.io/astral-sh/uv:python3.13-trixie AS base

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy

WORKDIR /app
################################################################################

################################################################################
# target: Python only (lightweight).
FROM base AS python

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY python ./python

CMD [".venv/bin/scrapy", "runspider", "python/elo/bga_spider.py"]
################################################################################

################################################################################
# Helper: Rust.
FROM base AS rust-base

ENV PATH="/root/.cargo/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
################################################################################

################################################################################
# target: Rust & Python (full).
FROM rust-base AS rust

COPY Cargo.toml Cargo.lock* ./
COPY pyproject.toml uv.lock ./
COPY rust ./rust
COPY python ./python

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    uv sync --locked

CMD ["uv", "run", "scrapy", "runspider", "python/elo/bga_spider.py"]
################################################################################
