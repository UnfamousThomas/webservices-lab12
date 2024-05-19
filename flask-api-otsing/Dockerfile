FROM python:3.8-slim


RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app
RUN mkdir -p /raamatud

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt
COPY hs10-flask-api-otsing.py app.py
EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
