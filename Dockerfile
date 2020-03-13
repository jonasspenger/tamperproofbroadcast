FROM alpine

EXPOSE 3489
EXPOSE 3490

RUN apk add python3

RUN echo "@testing http://nl.alpinelinux.org/alpine/edge/testing" | tee -a /etc/apk/repositories
RUN apk update
RUN apk add --update py3-grpcio@testing

RUN pip3 install --upgrade pip
RUN pip3 install --trusted-host pypi.python.org etcd3
RUN pip3 install --trusted-host pypi.python.org flask

WORKDIR /app
COPY . /app

CMD python3 app/app.py
