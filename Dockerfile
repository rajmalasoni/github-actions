FROM python:3.8-slim-buster
WORKDIR /
COPY main.py ./
CMD [ "python", "./main.py"]