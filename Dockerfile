FROM quay.io/cdis/python:python3.9-buster-2.0.0

RUN apt-get update \
     && apt-get install -y --no-install-recommends\
     ca-certificates \
     gcc \
     curl bash git vim \
     musl-dev \
     libffi-dev

RUN pip install --upgrade pip poetry

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY . /src/
WORKDIR /src
RUN python -m venv /env && . /env/bin/activate && poetry install --no-interaction --without dev

FROM quay.io/cdis/python:python3.9-buster-2.0.0

RUN apt-get update \
     && apt-get install -y --no-install-recommends\
     ca-certificates \
     gcc \
     curl bash git vim \
     musl-dev \
     libffi-dev

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1

COPY --from=builder /env /env
COPY --from=builder /src /src
ENV PATH="/env/bin/:${PATH}"

WORKDIR /src

CMD ["/env/bin/gunicorn", "-b", "0.0.0.0:80", "-k", "uvicorn.workers.UvicornWorker", "--timeout", "1800", "thor.main:app"]