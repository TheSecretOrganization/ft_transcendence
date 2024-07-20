FROM nginx:1.26.1

COPY conf/nginx.conf /etc/nginx/conf.d/default.conf

# COPY src /usr/share/nginx

# RUN chmod 755 -R /usr/share/nginx
# RUN chown -R www-data:www-data /usr/share/nginx

VOLUME [ "/usr/share/nginx" ]
EXPOSE 80

CMD [ "nginx", "-g", "daemon off;" ]
