FROM python:2.7
MAINTAINER garito@gmail.com

RUN apt-get update && apt-get install -y git

RUN useradd -ms /bin/bash ereuse

WORKDIR /home/ereuse
RUN git clone https://github.com/Garito/WorkbenchFS.git
WORKDIR /home/ereuse/WorkbenchFS

RUN pip install -r ./requirements.txt

USER ereuse

ENV FLASK_APP=app.py

EXPOSE 5000

CMD ["flask", "run", "-h", "0.0.0.0"]
