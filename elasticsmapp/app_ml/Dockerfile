FROM python:3.6-jessie

RUN apt-get update

WORKDIR ./machinelearning
ADD machinelearning/requirements.txt .
ADD machinelearning/glove-twitter-100.txt .
RUN pip install -r requirements.txt

RUN pip install git+https://github.com/crazyfrogspb/elasticsmapp
ADD machinelearning/.env .
ADD machinelearning/app.py .
ADD machinelearning/config.py .
ADD machinelearning/templates/ templates/
RUN python -m nltk.downloader stopwords
RUN pip install gunicorn

ENV PORT 8080
CMD ["gunicorn", "app:app", "--config=config.py"]
