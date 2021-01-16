FROM python:buster

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY / .

CMD ["python", "./main.py"]