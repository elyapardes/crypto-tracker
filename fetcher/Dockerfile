FROM python:3.9-alpine
WORKDIR .
COPY requirements.txt /fetcher/requirements.txt
# Fixes weird PEP 517 error
RUN apk add --no-cache gcc musl-dev linux-headers
RUN pip install -r /fetcher/requirements.txt
COPY . /fetcher
ENTRYPOINT ["python"]
CMD ["-u", "-m", "fetcher.main"]
