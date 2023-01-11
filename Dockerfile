FROM python:3.8-slim-buster
WORKDIR /

# Install & use pipenv
# COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install PyGithub
RUN pip3 install PyGithub


COPY main.py ./
# CMD [ "python", "/main.py"]
# CMD pipenv run python ./main.py
CMD ["pipenv", "run", "python", "/main.py"]
# RUN pipenv run python main.py