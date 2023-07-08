# FROM python:3
FROM ubuntu:latest

RUN apt-get update -qq && apt-get install ffmpeg -y
RUN apt-get install pip -y
RUN apt-get install python3 -y

# RUN apt-get update
# RUN apt-get upgrade -y
# RUN apt-get install python3.8 -y
# RUN apt-get install python3-pip -y

RUN ln -s /usr/bin/python3.8 /usr/bin/python

WORKDIR /discord-nagant 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["python3", "-u", "bot.py"]