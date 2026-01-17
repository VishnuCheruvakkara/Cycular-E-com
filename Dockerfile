FROM python:3.12-slim

RUN apt-get update && apt-get install -y nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# IMPORTANT: collect static during build
RUN python manage.py collectstatic --noinput

CMD sh -c "gunicorn cycular_ecommerce.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -"
