FROM python:3.11-slim
WORKDIR /code
COPY ./app /code/app
RUN pip install fastapi uvicorn[standard] psycopg2-binary python-dotenv sqlalchemy
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]