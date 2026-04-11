FROM python:3.10

WORKDIR /app

# Copy requirements first (fast build caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]