FROM python:3.12-slim

RUN apt-get update && apt-get install -y nano

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
