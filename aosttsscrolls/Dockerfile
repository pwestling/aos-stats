FROM jekyll/jekyll:latest
ADD ./ /var/www/
WORKDIR /var/www
RUN chmod -R a+rwx /var/www
RUN jekyll build
ENTRYPOINT ["jekyll", "serve", "-Vw","--incremental", "--skip-initial-build", "--no-watch", "--port", "8080"]
