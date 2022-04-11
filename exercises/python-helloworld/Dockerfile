FROM python:3-windowsservercore

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

CMD ["python","app.py"]