FROM python:3.11-slim

# Только базовые библиотеки для SSL
RUN apt-get update && apt-get install -y libssl-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TF_CPP_MIN_LOG_LEVEL=3
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]