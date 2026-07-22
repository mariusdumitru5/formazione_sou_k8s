FROM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir -r requirements.txt
 
FROM builder AS dev-envs

COPY . /app

ENTRYPOINT ["python3"]

CMD ["app.py"]

