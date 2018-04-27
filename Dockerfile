FROM ubuntu:xenial

RUN apt-get update; apt-get install -y python3 virtualenv python3-pip libev-dev

RUN mkdir /app

WORKDIR /app

RUN virtualenv -p python3 ./

ADD ./* ./

RUN bash -c "source bin/activate; pip install -r requirements.txt"

ADD fonts ./fonts

ADD static ./static

CMD bash -c "source bin/activate; python run.py"
