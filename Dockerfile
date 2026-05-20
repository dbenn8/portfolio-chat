# Stage 1: Build Astro portfolio site
FROM node:20-slim AS frontend
WORKDIR /app/portfolio
COPY portfolio/ .
RUN npm ci && npm run build

# Stage 2: Python API + static portfolio + widget
FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY ingest.py .
COPY rag-content/ ./rag-content/
COPY widget/widget.js ./static/widget.js
COPY --from=frontend /app/portfolio/dist ./static

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
