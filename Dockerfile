FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY src ./src

# Expose + run
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "iacp_core.app:app", "--host", "0.0.0.0", "--port", "8000"]
