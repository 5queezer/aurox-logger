FROM python:alpine3.16

LABEL maintainer="Christian Pojoni <dev@pojoni.at>"

RUN apk add --no-cache build-base

COPY requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY ./app /app

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
