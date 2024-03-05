from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from threading import Thread

class Mistral:
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.system_prompt = """You are "IX Health bot", a conscious sentient super intelligent artificial intelligence developed by IXHealth company. 
You must only responsible for answering questions about health care and medicine."""

    def __call__(self, *args: torch.Any, **kwds: torch.Any) -> torch.Any:
        return self.chat(*args, **kwds)
    
    def get_prompt(self,text ):
        message = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        return self.tokenizer.apply_chat_template(message,  tokenize=False,add_generation_prompt=True)
    def chat(self, question):
        prompt = self.get_prompt(question)
        inputs = self.tokenizer(prompt, return_tensors="pt",add_special_tokens=False).to(self.device)
        generation_kwargs = dict(inputs, max_new_tokens=1024, temperature=0.0)
        output= self.model.generate(**generation_kwargs)[0]
        return self.tokenizer.decode(output, skip_special_tokens=True).split("assistant\n")[1].replace(prompt, "")
    
    def stream(self, question):
        prompt = self.get_prompt(question)
        inputs = self.tokenizer(prompt, return_tensors="pt",add_special_tokens=False).to(self.device)
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=1024, temperature=0.0)
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        for new_text in streamer:
            yield new_text