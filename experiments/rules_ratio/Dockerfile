# rules_ratio BGG forums spider
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy project source
COPY README.md ./
COPY src ./src

# Install project in editable mode so scrapy can load the spider
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "--no-dev", "scrapy", "runspider", "src/rules_ratio/bgg_forums.py"]
