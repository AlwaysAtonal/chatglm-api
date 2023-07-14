FROM python:3.10.9

WORKDIR /chatglm-api

ADD ./app /chatglm-api/app
ADD ./requirements.txt /chatglm-api/requirements.txt
ADD ./log.json /chatglm-api/log.json

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install python3 python3-pip curl iputils-ping -y \
    && apt-get autoclean && rm -rf /var/lib/apt/lists/*

RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt --no-cache-dir \
    && rm -rf /root/.cache/pip/*
