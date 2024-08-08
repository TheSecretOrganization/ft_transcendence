FROM postgres:16.3

ARG POSTGRES_USER
ENV POSTGRES_USER=${POSTGRES_USER}

EXPOSE 5432

RUN apt update && apt upgrade -y

RUN groupadd -r appGroup && useradd -r -g appGroup ${POSTGRES_USER}
RUN chown ${POSTGRES_USER}:appGroup /var/lib/postgresql/data

USER ${POSTGRES_USER}

CMD ["postgres"]
