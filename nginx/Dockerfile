FROM nginx:1.26.1

RUN apt update -y && apt upgrade -y

COPY src /usr/share/nginx
COPY conf/nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod 755 -R /usr/share/nginx
RUN chown -R www-data:www-data /usr/share/nginx

VOLUME [ "/usr/share/nginx" ]
EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]
