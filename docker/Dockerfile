FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY REQUIREMENTS.TXT ./
RUN pip install --no-cache-dir -r REQUIREMENTS.TXT
COPY src/ ./src/
ENV PYTHONPATH=/app/src \
    SERVER_HOST=0.0.0.0 \
    SERVER_PORT=8207
EXPOSE 8207
WORKDIR /app/src
CMD ["python","-m","uvicorn","main:app","--host","0.0.0.0","--port","8207"]
