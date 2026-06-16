FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc build-essential && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml /pyproject.toml
RUN uv pip install --system --no-editable -r /pyproject.toml

COPY . .

CMD ["python", "worker/main.py"]
