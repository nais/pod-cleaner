FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user

COPY cleanup.py .

ENTRYPOINT [ "python", "cleanup.py" ]