FROM nginx:1.26.1

EXPOSE 80
VOLUME [ "/usr/share/nginx" ]

RUN apt update && apt upgrade -y

COPY conf/nginx.conf /etc/nginx/conf.d/default.conf

CMD [ "nginx", "-g", "daemon off;" ]
