FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN pip3 install psycopg2-binary SQLAlchemy
RUN chmod +x ./run.sh