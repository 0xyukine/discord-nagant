FROM ubuntu:latest
WORKDIR /bot

RUN apt-get update -qq && apt-get install ffmpeg python3 pip -y
RUN ln -s /usr/bin/python3.8 /usr/bin/python

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /temp

CMD ["python3", "-u", "bot.py"]
