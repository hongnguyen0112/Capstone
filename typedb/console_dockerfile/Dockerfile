FROM vaticle/typedb:latest

WORKDIR /app

COPY ./typedb ./

USER root

ENTRYPOINT [ "./typedb" ]

CMD ["console", "--server=typedb-server:1729", "--script=script.sh" ]