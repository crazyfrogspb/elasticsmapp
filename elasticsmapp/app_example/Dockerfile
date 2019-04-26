FROM python:3.6-jessie

RUN apt update

WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt



ENV PORT 8080
CMD ["gunicorn", "app:app", "--config=app/config.py"]
