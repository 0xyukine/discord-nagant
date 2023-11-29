FROM ubuntu:latest
WORKDIR /bot

RUN apt-get update -qq && apt-get install ffmpeg python3 pip git -y
RUN ln -s /usr/bin/python3.8 /usr/bin/python

COPY requirements.txt requirements.txt
COPY thread-watcher/ thread-watcher/
RUN pip install -r requirements.txt
RUN pip install -e thread-watcher/
#RUN python -m pip install git+https://github.com/0xyukine/thread-watcher
RUN mkdir /temp

CMD ["python3", "-u", "bot.py"]
