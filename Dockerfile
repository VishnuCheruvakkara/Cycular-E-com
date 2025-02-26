FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# Install system dependencies for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
