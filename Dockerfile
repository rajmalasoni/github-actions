FROM python:3.8-slim-buster
WORKDIR /chatops
COPY . .
RUN pip install pipenv && \
    pipenv install
CMD pipenv run python main.py
