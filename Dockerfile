FROM python:3.8-slim-buster
WORKDIR /chatops
COPY . .
RUN chmod u+x script.sh
RUN ./script.sh
#CMD ["/bin/bash", "./chatops/script.sh"]
