FROM vaticle/typedb:latest

WORKDIR /app

COPY ./typedb/wait-for-it.sh ./

COPY ./typedb/docker-entrypoint.sh ./

RUN chmod +x wait-for-it.sh docker-entrypoint.sh

COPY ./typedb ./

USER 1000

ENTRYPOINT [ "./docker-entrypoint.sh" ]

CMD ["./typedb","console", "--server=typedb-server:1729", "--script=script.sh" ]