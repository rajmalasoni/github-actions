FROM python:3.8-slim-buster
WORKDIR /
RUN pip install requests
COPY main.py ./
CMD [ "python", "/main.py"]