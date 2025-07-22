ARG AZLINUX_BASE_VERSION=master

# ------ Base stage ------
FROM quay.io/cdis/python-nginx-al:${AZLINUX_BASE_VERSION} AS base

ENV appname=thor

WORKDIR /${appname}

RUN chown -R gen3:gen3 /${appname}

# ------ Builder stage ------
FROM base AS builder

USER gen3

COPY poetry.lock pyproject.toml /$appname/
RUN pip install --upgrade pip poetry \
    && poetry install -vv --no-root --only main --no-interaction

COPY --chown=gen3:gen3 . /$appname
RUN poetry install --without dev --no-interaction

CMD ["gunicorn", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]