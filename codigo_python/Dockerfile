FROM python:3.8.7-slim-buster

RUN apt-get update && apt install -y iputils-ping

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3"]