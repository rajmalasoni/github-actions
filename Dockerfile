# Container image that runs your code
FROM python:latest

# ADD script.py /
# Copies your code file from your action repository to the filesystem path `/` of the container
COPY main.py .


# Code file to execute when the docker container starts up (`entrypoint.sh`)
CMD ["python", "main.py"]
