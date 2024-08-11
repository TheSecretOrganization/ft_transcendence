FROM nginx:1.26.1

ARG HOSTNAME
ENV HOSTNAME=${HOSTNAME}

EXPOSE 443
VOLUME [ "/usr/share/nginx" ]

RUN apt update && \
    apt upgrade -y

COPY conf/default.conf /etc/nginx/conf.d/default.conf.template
RUN envsubst '${HOSTNAME}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

CMD [ "nginx", "-g", "daemon off;" ]
