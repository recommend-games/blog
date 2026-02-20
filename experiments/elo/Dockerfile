# target: scraper — deps from uv.lock only, no project/Rust. For bga-spider.
FROM ghcr.io/astral-sh/uv:python3.13-trixie AS python

ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY python ./python

CMD ["uv", "run", "scrapy", "runspider", "python/elo/bga_spider.py"]

# target: full — scraper + Rust + project (maturin). For code that uses elo._rust.
FROM python AS rust

ENV PATH="/root/.cargo/bin:$PATH"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY Cargo.toml Cargo.lock* ./
COPY rust ./rust
COPY python ./python

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    uv sync --locked

CMD ["uv", "run", "scrapy", "runspider", "python/elo/bga_spider.py"]
