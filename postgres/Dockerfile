FROM postgres:16.3

ARG POSTGRES_USER
ENV POSTGRES_USER=${POSTGRES_USER}

ENV PGDATA=/data/pgdata
ENV POSTGRES_INITDB_ARGS="-D ${PGDATA}"

EXPOSE 5432

RUN apt update && \
    apt upgrade -y

RUN groupadd -r appGroup && \
    useradd -r -g appGroup ${POSTGRES_USER} && \
    mkdir -p ${PGDATA} && \
    chown ${POSTGRES_USER}:appGroup ${PGDATA} && \
    chmod 766 ${PGDATA}

USER ${POSTGRES_USER}

CMD ["postgres"]
