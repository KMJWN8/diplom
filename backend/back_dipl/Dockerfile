FROM python:3.10.12-slim

ENV HTTP_PROXY=http://10.0.113.16:1118/
ENV HTTPS_PROXY=http://10.0.113.16:1118/

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]



