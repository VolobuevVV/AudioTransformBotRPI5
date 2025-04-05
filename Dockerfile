FROM balenalib/raspberrypi5-alpine-python:latest

RUN apk update && apk add --no-cache \
    build-base \
    ffmpeg \
    libmagic \
    libffi-dev \
    zlib-dev \
    jpeg-dev \
    bash \
    && rm -rf /var/cache/apk/*

RUN python3 -m ensurepip --upgrade && \
    pip3 install --no-cache-dir --upgrade pip

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /root/

ENTRYPOINT ["python3", "main.py"]
