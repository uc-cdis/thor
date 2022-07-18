FROM quay.io/cdis/python:3.8-buster as base

FROM base as builder
RUN pip install --upgrade pip poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc g++ musl-dev libffi-dev libgit2-dev libssl-dev make postgresql git curl

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY . /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && poetry install --no-interaction --no-dev

FROM base
COPY --from=builder /env /env
COPY --from=builder /src /src
ENV PATH="/env/bin/:${PATH}"
WORKDIR /src

CMD ["/env/bin/gunicorn", "thor.main:app", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker"]
CMD psql -U postgres -c "create database thor_test_tmp"
CMD python thor/create_all_tables.py
