FROM python:3.6-jessie

RUN apt-get update

WORKDIR .
ADD requirements.txt .
RUN pip install -r requirements.txt

COPY glove-twitter-100.txt .
ADD __init__.py .
ADD config.py .
ADD app.py .
ADD  .env .
ADD templates/ templates/

RUN pip install git+https://github.com/crazyfrogspb/elasticsmapp
RUN python -m nltk.downloader stopwords
RUN pip install gunicorn

ENV PORT 8080
CMD ["gunicorn", "app:app", "--config=config.py"]