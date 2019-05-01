FROM python:3.6-jessie

RUN apt update

WORKDIR ./machinelearning
ADD machinelearning/requirements.txt .
RUN pip install -r requirements.txt

RUN pip install git+https://github.com/crazyfrogspb/elasticsmapp
ADD machinelearning/ .

ENV PORT 8080
RUN python -c "import elasticsmapp.utils.text_utils"
CMD ["gunicorn", "app:app", "--config=config.py"]
