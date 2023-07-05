FROM python:3

WORKDIR /discord-nagant 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "-u", "bot.py"]