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

RUN sudo -H pip3 install gdown
RUN gdown https://drive.google.com/uc?id=1mPlhwM47Ub3SwQyufgFj3JJ9oB_wrU5D
RUN sudo -H pip3 install torch-2.0.0a0+gite9ebda2-cp39-cp39-linux_aarch64.whl
RUN rm torch-2.0.0a0+gite9ebda2-cp39-cp39-linux_aarch64.whl

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "main.py"]
