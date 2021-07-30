FROM rasa/rasa-sdk:2.7.0

WORKDIR /app

COPY ./requirements.txt ./

COPY ./schema.py ./

COPY ./graph_database.py ./

USER root

COPY ./actions /app/actions

RUN pip3 install -r requirements.txt

USER 1000


