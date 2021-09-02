FROM python:3.8.6-slim

COPY requirements.txt /requirements.txt

COPY test.requirements.txt /test.requirements.txt


RUN pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    pip install -r /test.requirements.txt && \
    rm -rf /.cache/pip*

COPY ./app /app

CMD [ "pytest", "/app" ]
