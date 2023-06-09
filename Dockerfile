FROM cgr.dev/chainguard/python:3.10-dev as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user

FROM cgr.dev/chainguard/python:3.10

WORKDIR /app

# Make sure you update Python version in path
COPY --from=builder /home/nonroot/.local/lib/python3.10/site-packages /home/nonroot/.local/lib/python3.10/site-packages

COPY cleanup.py .

ENTRYPOINT [ "python", "/app/cleanup.py" ]