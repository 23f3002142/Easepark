FROM python:3.11-slim

WORKDIR /app

# Install dependencies for psycopg2 (Postgres driver)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add Gunicorn for production use
RUN pip install gunicorn

COPY . .

EXPOSE 5000

# Default command → dev server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
