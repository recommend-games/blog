# Build and run the BGA Scrapy spider with uv (Python 3.13 + Rust for maturin).
FROM ghcr.io/astral-sh/uv:python3.13-trixie

# Install Rust for building the elo package (maturin/Rust extension).
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Install dependencies only (no project). This layer is cached until pyproject.toml/uv.lock change.
COPY pyproject.toml uv.lock ./
ENV UV_NO_DEV=1
ENV UV_LINK_MODE=copy
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

# Copy project source; then install project (maturin build). Only this layer reruns on code changes.
COPY Cargo.toml Cargo.lock* ./
COPY rust ./rust
COPY python ./python
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    uv sync --locked

CMD ["uv", "run", "scrapy", "runspider", "python/elo/bga_spider.py"]
