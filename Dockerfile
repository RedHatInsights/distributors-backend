FROM registry.access.redhat.com/ubi9/python-312:9.6-1760372467 AS builder

COPY --chown=1001:0 . /app-src
RUN pip install --no-cache-dir /app-src

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6-1760515502

ENV VIRTUAL_ENV='/opt/app-root'
ENV APP_SRC='/app-src'
ENV PORT=8000

RUN microdnf install -y python3.12 \
    && microdnf clean all

RUN mkdir $APP_SRC && chown 1001:0 $APP_SRC

USER 1001

COPY --from=builder  /opt/app-root $VIRTUAL_ENV
COPY --from=builder  /app-src $APP_SRC

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app-src

ENTRYPOINT ["sh", "-c", "fastapi run /app-src/src/main.py --port $PORT"]
