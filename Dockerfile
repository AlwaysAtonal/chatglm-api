FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

WORKDIR /chatglm-api

ADD ./app /chatglm-api/app
ADD ./requirements.txt /chatglm-api/requirements.txt

RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.ustc.edu.cn@g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install python3 python3-pip -y \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir \
    && rm -rf /root/.cache/pip/*
