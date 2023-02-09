FROM python:3.7
WORKDIR /app
COPY / /app
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5000
#ENV FLASK_APP=app.py

#RUN flask db init
#RUN flask db migrate
#RUN flask db upgrade

RUN ./init_db.sh

RUN python -m unittest discover

CMD ["flask", "run", "--host=0.0.0.0"]
