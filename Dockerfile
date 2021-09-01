FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    rm -rf /.cache/pip*

COPY ./app /app
