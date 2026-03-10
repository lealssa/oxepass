FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

# Copy application
COPY app/ ./app/

# Run with gunicorn
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app.app:app"]
