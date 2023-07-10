from transformers import AutoTokenizer, AutoModel
from .types import ChatGLMRequest
from ..config import env

def verification(request: ChatGLMRequest):
    '''避免出现 None 值的情况'''
    request.max_length = request.max_length if request.max_length else 2048
    request.temperature = request.temperature if request.temperature else 0.95
    request.top_p = request.top_p if request.top_p else 0.7
    return request

class ChatGLM_6B:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            env.model_path, 
            trust_remote_code=True
        )

        self.model = AutoModel.from_pretrained(
            env.model_path, 
            trust_remote_code=True
        ).half().cuda()

        self.model.eval()

    def __call__(self):
        return self
    
    def chat(self, params: ChatGLMRequest):
        '''返回 chatglm-6b 输出结果'''
        params = verification(params)
        return self.model.chat(
            self.tokenizer,
            params.prompt,
            history = params.history,
            max_length = params.max_length,
            top_p = params.top_p,
            temperature = params.temperature
        )
    
    def chat_stream(self, params: ChatGLMRequest):
        '''返回 chatglm-6b 流式输出结果'''
        params = verification(params)
        pos = 0
        for response, _ in self.model.stream_chat(
            self.tokenizer, 
            params.prompt, 
            history = params.history,
            max_length = params.max_length,
            top_p = params.top_p,
            temperature = params.temperature
        ):
            try:
                data = response[pos:]
                pos = len(response)
                yield data
            except:
                continue