FROM python:3.8-slim-buster

RUN python -m pip install --upgrade pip
COPY main.py ./
COPY requirements.txt ./
RUN python3 -m venv .venv
RUN pip install -r requirements.txt

CMD ["python", "/main.py"]
