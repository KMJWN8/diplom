FROM python:3.11

WORKDIR /app

ENV HTTP_PROXY="http://10.0.219.4:1118"

ENV HTTPS_PROXY="http://10.0.219.4:1118"

ENV NO_PROXY="localhost,127.0.0.1"

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .env /app/.env

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]