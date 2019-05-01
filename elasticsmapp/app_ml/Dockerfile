FROM python:3.6-jessie

RUN apt update

WORKDIR ./machinelearning
ADD machinelearning/requirements.txt .
RUN pip install -r requirements.txt
RUN git clone https://github.com/crazyfrogspb/elasticsmapp
RUN cd elasticsmapp
RUN ls
RUN pip install -e .
RUN cd ..
ADD machinelearning/ .

ENV PORT 8080
CMD ["gunicorn", "app:app", "--config=config.py"]
