FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app/src SUPPLYCHAIN_DB=/data/control_center.sqlite3
VOLUME ["/data"]
EXPOSE 8000
CMD ["uvicorn", "supplychain.main:app", "--host", "0.0.0.0", "--port", "8000"]
