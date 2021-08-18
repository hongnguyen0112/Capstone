FROM rasa/rasa:2.7.1

WORKDIR /app

COPY ./requirements.txt ./

COPY ./wait-for-it.sh  ./

COPY ./docker-entrypoint.sh  ./

COPY ./migration_script.sh ./

USER root

COPY . /app

RUN pip3 install -r requirements.txt

RUN chmod +x wait-for-it.sh docker-entrypoint.sh

USER 1000

ENTRYPOINT [ "./docker-entrypoint.sh" ]

CMD ["rasa","shell"]
