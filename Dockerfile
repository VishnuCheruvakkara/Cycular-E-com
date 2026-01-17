FROM python:3.12-slim

RUN apt-get update && apt-get install -y nano

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway provides PORT at runtime
CMD sh -c "gunicorn cycular_ecommerce.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
