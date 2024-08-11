FROM postgres:16.3

ARG POSTGRES_USER
ENV POSTGRES_USER=${POSTGRES_USER}

ENV PGDATA=/data/pgdata

EXPOSE 5432

RUN apt update && \
    apt upgrade -y

RUN mkdir -p ${PGDATA} && \
    groupadd -r appGroup && \
    useradd -r -g appGroup ${POSTGRES_USER} && \
    chown ${POSTGRES_USER}:appGroup ${PGDATA}

USER ${POSTGRES_USER}

CMD ["postgres"]
