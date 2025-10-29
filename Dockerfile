ARG AZLINUX_BASE_VERSION=3.13-pythonnginx

FROM quay.io/cdis/amazonlinux-base:${AZLINUX_BASE_VERSION} AS base

USER root
# Install vim and findutils (which provides `find`)
RUN dnf install -y vim findutils jq && \
    dnf install -y openssl && \
    dnf clean all && \
    rm -rf /var/cache/dnf

COPY --chown=gen3:gen3 . /src

WORKDIR /src

USER gen3

RUN ls -ltr /usr/bin/python*
#RUN poetry install --no-interaction --only main

#CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]