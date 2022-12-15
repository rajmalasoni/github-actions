FROM python:3-slim AS builder
COPY main.py /app
WORKDIR /app
CMD ["/app/main.py"]