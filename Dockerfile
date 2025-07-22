ARG AZLINUX_BASE_VERSION=master

FROM quay.io/cdis/python-nginx-al:${AZLINUX_BASE_VERSION}

ENV appname=thor

USER gen3

WORKDIR /${appname}

COPY --chown=gen3:gen3 . /$appname

RUN pip install --upgrade pip poetry \
    && poetry install -vv --no-root --only main --no-interaction

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]