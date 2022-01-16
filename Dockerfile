# Docker image for https://github.com/TheAwiteb/satr-statistics-maker

FROM python:3.8

# install git
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git

# clone satr-statistics-maker repo
RUN git clone https://github.com/TheAwiteb/satr-statistics-maker

WORKDIR ./satr-statistics-maker

RUN pip3 install -r ./requirements.txt

CMD [ "python3", "ssma", "--prompt" ]
