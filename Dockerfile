FROM ubuntu:18.04
RUN apt-get update \
        && apt-get install nano && apt-get install -y maven 
RUN apt-get install -y python3.5 python3-pip python3-setuptools
WORKDIR /data
ADD ./GraphFactorization /data
RUN pip3 install -r /data/requirements.txt
CMD ["tail", "-f", "/dev/null"]
