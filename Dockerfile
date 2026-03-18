# ── Stage 1: Build Tailwind CSS ──
FROM node:22-slim AS css

WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci
COPY app/static/css/input.css app/static/css/input.css
COPY app/templates/ app/templates/
RUN npx @tailwindcss/cli -i app/static/css/input.css -o app/static/css/tailwind.css --minify

# ── Stage 2: Python app ──
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Copy application
COPY app/ ./app/

# Copy built CSS from stage 1
COPY --from=css /build/app/static/css/tailwind.css ./app/static/css/tailwind.css

# Run with gunicorn
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app.app:app"]
