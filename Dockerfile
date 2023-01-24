FROM python:3.8-slim-buster
WORKDIR /chatops
COPY . .
RUN pip install pipenv
CMD cd /chatops && pipenv install && pipenv run python main.py
