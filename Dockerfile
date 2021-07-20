FROM rasa/rasa-sdk:2.7.0

WORKDIR /app

COPY actions/requirements.txt ./

USER root

COPY ./actions /app/actions

RUN pip3 install -r requirements.txt

USER 1000

CMD ["start"]

