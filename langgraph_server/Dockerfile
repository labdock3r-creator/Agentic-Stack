FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y build-essential g++ && rm -rf /var/lib/apt/lists/*
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
