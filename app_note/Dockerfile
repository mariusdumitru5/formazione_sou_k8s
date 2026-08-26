FROM python:3.11-alpine AS builder

WORKDIR /app

COPY requirements.txt /app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

FROM builder AS dev-envs

# Copia i file e le directory dalla cartella corrente (app.py, templates, instance)
COPY app.py /app/
COPY templates/ /app/templates

ENTRYPOINT ["python3"]

CMD ["app.py"]