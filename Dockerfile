FROM balenalib/raspberrypi4-64-debian:bullseye

WORKDIR /root/

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget build-essential libssl-dev zlib1g-dev libncurses5-dev libreadline-dev \
    libsqlite3-dev libgdbm-dev libbz2-dev libexpat1-dev liblzma-dev \
    libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libatlas-base-dev gfortran \
    cmake git unzip ccache \
    ffmpeg \
    v4l2loopback-utils \
    ocl-icd-libopencl1 clinfo && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/ccache /usr/local/bin/cc

RUN wget https://www.python.org/ftp/python/3.9.14/Python-3.9.14.tgz && \
    tar xzf Python-3.9.14.tgz && \
    cd Python-3.9.14 && \
    ./configure --enable-optimizations --with-lto && \
    make -j$(nproc) altinstall && \
    cd .. && \
    rm -rf Python-3.9.14 Python-3.9.14.tgz

RUN wget https://bootstrap.pypa.io/get-pip.py && python3.9 get-pip.py && rm get-pip.py

RUN pip3.9 install gdown
RUN pip3.9 install setuptools==58.3.0
RUN pip3.9 install Cython

RUN gdown https://drive.google.com/uc?id=1mPlhwM47Ub3SwQyufgFj3JJ9oB_wrU5D
RUN pip3.9 install torch-2.0.0a0+gite9ebda2-cp39-cp39-linux_aarch64.whl
RUN rm torch-2.0.0a0+gite9ebda2-cp39-cp39-linux_aarch64.whl

COPY requirements.txt ./
RUN pip3.9 install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y libopenmpi-dev && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y libopenblas-base && rm -rf /var/lib/apt/lists/*
COPY . .

ENTRYPOINT ["python3.9", "main.py"]
