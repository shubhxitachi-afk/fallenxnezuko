FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       ffmpeg \
       git \
       gcc \
       python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -U pip setuptools
RUN pip3 install -U -r requirements.txt

CMD ["python3", "-m", "FallenRobot"]
