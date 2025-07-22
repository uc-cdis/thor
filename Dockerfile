ARG AZLINUX_BASE_VERSION=master

# ------ Base stage ------
FROM quay.io/cdis/python-nginx-al:${AZLINUX_BASE_VERSION} AS base

COPY --chown=gen3:gen3 . /src

WORKDIR /src

# ------ Builder stage ------
FROM base AS builder

USER gen3

RUN poetry install --no-interaction --only main

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]