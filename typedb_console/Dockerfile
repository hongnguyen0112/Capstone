FROM vaticle/typedb:latest

WORKDIR /app

COPY ./typedb ./app

USER root

ENTRYPOINT [ "./typedb" ]

CMD ["console", "--server=typedb-server:1729", "--script=script.sh" ]