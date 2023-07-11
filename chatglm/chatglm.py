#!/usr/bin/env python
# coding=utf-8
## From: https://github.com/THUDM/ChatGLM-6B
import time
import torch
import os
from typing import Dict, Union, Optional
from torch.nn import Module
from transformers import AutoModel, AutoTokenizer
from .chat import do_chat, do_chat_stream
from utils import load_model_on_gpus


def init_chatglm(model_path: str, running_device: str, gpus: int):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if running_device.upper() == "GPU":
        model = load_model_on_gpus(model_path, gpus)
    else:
        model = AutoModel.from_pretrained(model_path, trust_remote_code=True)
        model = model.float()
    model.eval()
    model.do_chat = do_chat
    model.do_chat_stream = do_chat_stream
    return tokenizer, model