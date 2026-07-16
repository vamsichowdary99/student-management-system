# python:3.11-slim keeps the image small; mysql-connector-python is pure
# Python (unlike mysqlclient), so no extra system build tools are needed.
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first so Docker caches this layer -- rebuilds after an
# app code change won't need to reinstall dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Gunicorn, not Flask's built-in dev server -- a small but real
# "production-ready" detail worth calling out in interviews.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]