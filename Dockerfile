FROM balenalib/raspberrypi5-alpine-python:latest
WORKDIR /root/
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

pip install torch-1.13.0+cpu-cp39-cp39-linux_armv7l.whl

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
