from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
import torch
from threading import Thread
model_name = "suzii/IX_health_mistral_7b_intrus_lora_v1.3"

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    low_cpu_mem_usage=True,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map={"": 0},
)

class Chatbot:
    def __init__(self, model=model, tokenizer=tokenizer, system_prompt=system_prompt):
        self.model = model
        self.tokenizer = tokenizer
        self.streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        self.system_prompt = system_prompt
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    def chat(self, text):
        message = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text}
        ]
        prompt = tokenizer.apply_chat_template(message,  tokenize=False,add_generation_prompt=True)
        inputs = tokenizer(prompt, return_tensors="pt",add_special_tokens=False).to(self.device)
        generation_kwargs = dict(inputs, streamer=self.streamer, max_new_tokens=1024)
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        for new_text in self.streamer:
            yield new_text
            
chatbot = Chatbot(model=model, tokenizer=tokenizer, system_prompt=system_prompt)

def run(question):
    for new_text in chatbot.chat(question):
        print(new_text)
run("who are you?")
