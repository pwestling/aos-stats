FROM ubuntu
RUN apt-get update
RUN apt-get install nginx -y
COPY nginx.conf /etc/nginx/sites-enabled/default
COPY _site/ /var/www/html/
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
