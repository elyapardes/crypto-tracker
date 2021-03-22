FROM python:3.9-alpine
WORKDIR .
COPY requirements.txt /service/requirements.txt
RUN pip3 install -r /service/requirements.txt
COPY . /service
ENTRYPOINT ["python"]
CMD ["-m", "service.api"]
