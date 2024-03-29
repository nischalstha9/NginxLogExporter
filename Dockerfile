FROM python:3.9-slim

RUN mkdir /code
WORKDIR /code

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./src/* .

EXPOSE 8000
ENTRYPOINT [ "python3", "main.py"]
