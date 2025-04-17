FROM python:3

RUN mkdir /webserver
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN pip3 install urllib3
RUN pip3 install requests
RUN pip3 install pyyaml
RUN pip3 install "fastapi[standard]"

RUN locale-gen en_US.UTF-8
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
ENV LC_ALL="en_US.UTF-8"
ENV LC_CTYPE="en_US.UTF-8"

RUN dpkg-reconfigure --frontend=noninteractive locales

COPY ./app/ /webserver

WORKDIR /webserver

EXPOSE 8000

CMD ["fastapi", "run", "server.py"]