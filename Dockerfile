FROM python:3.8-slim-buster
WORKDIR /chatops
COPY . .
CMD ["/bin/bash", "./script.sh"]
