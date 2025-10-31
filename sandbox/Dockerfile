FROM python:3.12-slim

WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY ./sandbox ./sandbox

ENV PYTHONPATH=/app/src
CMD ["python","-m","uvicorn","iacp_core.app:app","--host","0.0.0.0","--port","8001"]