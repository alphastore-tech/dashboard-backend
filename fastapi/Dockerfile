FROM python:3.11-slim
WORKDIR /fastapi
COPY ./app /fastapi/app

RUN pip install fastapi uvicorn[standard] psycopg2-binary python-dotenv sqlalchemy black
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]