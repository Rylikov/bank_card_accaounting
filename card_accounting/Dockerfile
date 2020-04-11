FROM python:3.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install --no-cache-dir psycopg2-binary
RUN pip install --no-cache-dir uWSGI
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["uwsgi","--http", ":8000", "--wsgi-file", "card_accounting/wsgi.py"]