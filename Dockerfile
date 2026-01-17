FROM python:3.12-slim

RUN apt-get update && apt-get install -y nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "
python manage.py collectstatic --noinput &&
gunicorn cycular_ecommerce.wsgi:application \
  --bind 0.0.0.0:$PORT \
  --workers 3 \
  --log-level debug \
  --access-logfile - \
  --error-logfile -
"
