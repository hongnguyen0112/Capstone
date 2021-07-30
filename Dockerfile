FROM rasa/rasa:2.7.1

WORKDIR /app

COPY ./requirements.txt ./

USER root

COPY . /app

RUN pip3 install -r requirements.txt

USER 1000

CMD ["shell"]
