FROM python:3.9.1

ENV SRC_DIR /usr/bin/src/webapp
ENV PYTHONUNBUFFERED=1

COPY . ${SRC_DIR}/
WORKDIR ${SRC_DIR}

RUN pip install -r requirements.txt

CMD ["python", "src/main.py"]
