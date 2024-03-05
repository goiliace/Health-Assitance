from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.memory.chat_message_histories import ZepChatMessageHistory

from transformers import AutoModelForCausalLM, AutoTokenizer

from search.google_search import GoogleSearch
from .mistral_7b import Mistral
from .prompt import PROMPT, PROMPT_WITH_CONTEXT
import torch

import os
import json
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join('.env')
load_dotenv(dotenv_path)

model_name = os.environ.get("MODEL_NAME")
ZEP_API_URL = os.environ.get("ZEP_API_URL")
model = AutoModelForCausalLM.from_pretrained(
            model_name,
            low_cpu_mem_usage=True,
            return_dict=True,
            torch_dtype=torch.float16,
            device_map={"": 0},
        )
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

class Chatbot:
    def __init__(self, ):
        self.llm = Mistral(model, tokenizer)
        self.search = GoogleSearch(k=5)
    def stream(self, question, session_id = "", internet_search = False):
        if session_id == "":
            session_id = "1234"
        zep = ZepChatMessageHistory(
            session_id=session_id,
            url=ZEP_API_URL,
        )
        memory = ConversationBufferWindowMemory(memory_key='chat_history',
                                             k=2,
                                            return_messages=True,
                                            chat_memory=zep,
                                            output_key='answer')
        chat_history = memory.load_memory_variables({})
        query = ""
        print("internet_search: ", internet_search)
        if internet_search:
            context = self.search.get_list(question)
            query = PROMPT_WITH_CONTEXT.format_prompt(chat_history=chat_history, context=json.dumps(context, indent=4), question=question).text
        else:
            context = None
            query = PROMPT.format_prompt(chat_history=chat_history, question=question).text
        print("prompt: ", query)
        content = ""
        for text in self.llm.stream(query):
            content += text
            yield text
        inputs = {'question': question, 'chat_history': chat_history}
        outputs = {'answer': content}
        memory.save_context(inputs, outputs)