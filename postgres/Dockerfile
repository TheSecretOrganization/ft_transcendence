FROM postgres:16.3

ENV PGDATA=/data/pgdata

EXPOSE 5432

RUN apt update && \
    apt upgrade -y

RUN mkdir -p ${PGDATA}

CMD ["postgres"]
