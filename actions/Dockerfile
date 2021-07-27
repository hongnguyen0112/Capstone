FROM rasa/rasa-sdk:2.7.0

WORKDIR /app

COPY ./requirements.txt ./

USER root

COPY ./ /app/actions

RUN pip3 install -r requirements.txt

USER 1000

CMD ["start"]

