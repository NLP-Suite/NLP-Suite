FROM alpine:3.19 as builder
MAINTAINER Arne Neumann <nlpbox.programming@arne.cl>

RUN apk update && apk add py3-pip wget

WORKDIR /opt

# install grepurl script to retrieve the most current download URL of CoreNLP.
# install latest CoreNLP release.
RUN pip install grepurl --break-system-packages && \
  wget `grepurl -r 'stanford-corenlp-.*\.zip' -a http://stanfordnlp.github.io/CoreNLP` && \
  unzip stanford-corenlp-*.zip && \
  mv $(ls -d stanford-corenlp-*/) corenlp && rm *.zip

# install latest English language model
#
# Docker can't store the result of a RUN command in an ENV, so we'll have
# to use this workaround.
# This command get's the first model file (at least for English there are two)
# and extracts its property file.
WORKDIR /opt/corenlp
RUN wget $(grepurl -r 'english.*jar$' -a http://stanfordnlp.github.io/CoreNLP | head -n 1)


# only keep the things we need to run and test CoreNLP
FROM alpine:3.19

RUN apk update && apk add openjdk8-jre-base py3-pip curl && \
  pip install pytest pexpect requests --break-system-packages

WORKDIR /opt/corenlp
COPY --from=builder /opt/corenlp .

ENV JAVA_XMX 4g
ENV TIMEOUT_MILLISECONDS 999999
ENV PORT 9000

EXPOSE $PORT

CMD java -mx$JAVA_XMX -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port $PORT -timeout $TIMEOUT_MILLISECONDS
