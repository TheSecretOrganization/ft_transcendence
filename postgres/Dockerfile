FROM postgres:16.3

ARG POSTGRES_USER
ENV POSTGRES_USER=${POSTGRES_USER}

ENV PGDATA=/data/pgdata

EXPOSE 5432

RUN apt update && \
    apt upgrade -y

RUN mkdir -p ${PGDATA}

CMD ["postgres"]
