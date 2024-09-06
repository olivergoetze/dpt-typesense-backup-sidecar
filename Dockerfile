FROM python:3.12-alpine
ENV RUN_USER=nobody
ENV RUN_GROUP=0

RUN pip install typesense cloudpathlib[s3]

COPY create_backup.py /opt/typesense_backup/create_backup.py
COPY crontab /opt/typesense_backup/crontab

RUN crontab /opt/typesense_backup/crontab

CMD ["crond", "-f"]