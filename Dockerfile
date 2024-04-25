FROM python:3
WORKDIR /bot

RUN apt-get update -qq && apt-get install ffmpeg python3 pip git -y

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /temp

CMD ["python", "-u", "bot.py"]