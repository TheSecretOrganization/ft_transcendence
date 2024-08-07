FROM nginx:1.26.1

ARG HOSTNAME
ENV HOSTNAME=${HOSTNAME}

ARG BASE_URL
ENV BASE_URL=${BASE_URL}

ARG API_BASE_URL
ENV API_BASE_URL=${API_BASE_URL}

EXPOSE 80
VOLUME [ "/usr/share/nginx" ]

RUN apt update && apt upgrade -y

COPY conf/nginx.conf.template /etc/nginx/nginx.conf.template
RUN envsubst '${BASE_URL}' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf

COPY conf/default.conf.template /etc/nginx/conf.d/default.conf.template
RUN envsubst '${HOSTNAME}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

COPY conf/config.json.template /tmp/config.json.template
RUN envsubst '${API_BASE_URL}' < /tmp/config.json.template > /usr/share/nginx/config.json

CMD [ "nginx", "-g", "daemon off;" ]
