#!/usr/bin/env python
# coding=utf-8
import argparse
import os
import sys
import toml
import uvicorn
from context import context


def main():
    parser = argparse.ArgumentParser(
        description='Start LLM and Embeddings models as a service.')
    parser.add_argument('--config', type=str, help='Path to the config file',
                        default='config.toml')
    parser.add_argument('--llm_model', type=str, help='Choosed LLM model',
                        default='chatglm2-6b')
    parser.add_argument('--embeddings_model', type=str,
                        help='Choosed embeddings model, can be empty',
                        default='')
    parser.add_argument('--device', type=str,
                        help='Device to run the service, gpu/cpu/mps',
                        default='gpu')
    parser.add_argument('--gpus', type=int, help='Use how many gpus, default 1',
                        default=2)
    parser.add_argument('--port', type=int, help='Port number to run the service',
                        default=8000)

    args = parser.parse_args()

    print("> Load config and arguments...")
    print(f"Config file: {args.config}")
    print(f"Language Model: {args.llm_model}")
    # print(f"Embeddings Model: {args.embeddings_model}")
    print(f"Device: {args.device}")
    print(f"GPUs: {args.gpus}")
    print(f"Port: {args.port}")

    with open(args.config) as f:
        config = toml.load(f)
        print(f"Config: \n{config}")
        context.tokens = config['auth']['tokens']

    if args.llm_model:
        print(f"> Start LLM model {args.llm_model}")
        if args.llm_model not in config['models']['llm']:
            print(f"LLM model {args.llm_model} not found in config file")
            sys.exit(1)
        llm = config['models']['llm'][args.llm_model]
        context.llm_model_type = llm['type']
        if llm['type'] == 'chatglm':
            print(f">> Use chatglm llm model {llm['path']}")
            from chatglm import init_chatglm
            context.tokenizer, context.model = init_chatglm(
                llm['path'], args.device, args.gpus)
        else:
            print(f"Unsupported LLM model type {llm['type']}")
            sys.exit(1)

    print("> Start API server...")

    from app import app
    uvicorn.run(app, host="0.0.0.0", port=args.port)


if __name__ == '__main__':
    main()
