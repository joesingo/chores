FROM tiangolo/uwsgi-nginx-flask:python3.11

COPY ./requirements.txt /app/requirements.txt
COPY ./chores.py /app/chores.py
COPY ./webapp.py /app/webapp.py
COPY ./static/ /app/static
COPY ./templates/ /app/templates

WORKDIR /app
RUN pip install --upgrade pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN echo "[uwsgi]" > uwsgi.ini
RUN echo "module = webapp" >> uwsgi.ini
RUN echo "callable = app" >> uwsgi.ini

ENV UWSGI_CHEAPER 0
ENV UWSGI_PROCESSES 1
ENV STATIC_PATH /app/static
