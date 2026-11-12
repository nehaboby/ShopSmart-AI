
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home appuser \
    && mkdir -p /app/instance \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--preload", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "run:app"]