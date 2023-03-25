FROM python:3.8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONBUFFERED 1
WORKDIR /usr/src/MyCRM
COPY ./requirements.txt /usr/src/MyCRM/requirements.txt
RUN pip install -r /usr/src/MyCRM/requirements.txt
COPY . /usr/src/MyCRM
#EXPOSE 8000
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["celery", "worker", "-A", "MyCRM", "--loglevel=info", "-P", "solo"]