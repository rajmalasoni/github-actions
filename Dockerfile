FROM python:3.8-slim-buster
WORKDIR /chatops
COPY . .
RUN ls -la
RUN chmod u+x script.sh
CMD ["/bin/bash", "./chatops/script.sh"]
