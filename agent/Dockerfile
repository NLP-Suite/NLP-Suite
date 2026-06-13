FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /nlp-suite

RUN apt-get update && apt-get install -y python3.9 python3.9-dev python3-pip python3-tk curl

RUN python3.9 -m pip install --upgrade pip && \
    python3.9 -m pip install setuptools

ENV STANZA_RESOURCES_DIR=/root/stanza_resources
ENV NLTK_DATA=/root/nltk_data

COPY requirements.txt .
RUN python3.9 -m pip install -r requirements.txt
RUN python3.9 -c "import stanza; stanza.download('en', model_dir='/root/stanza_resources')"
RUN python3.9 -c "import nltk; nltk.download('stopwords', download_dir='/root/nltk_data'); nltk.download('punkt', download_dir='/root/nltk_data')"

COPY . .




WORKDIR /nlp-suite/src
EXPOSE 3000
CMD ["python3.9", "main.py"]
