FROM python:3.12-slim

# Install basic utilities
RUN apt-get update && apt-get install -y nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies including whitenoise
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port (Railway provides $PORT env)
ENV PORT=8000

# Collect static files and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn cycular_ecommerce.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-level debug --access-logfile - --error-logfile -"]
