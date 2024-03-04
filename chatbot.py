import streamlit as st
import os
from constants import search_number_messages
from langchain_utils import initialize_chat_conversation
from search_indexing import download_and_index_pdf, get_faiss_index
from translatevien import translate_vi2en
from threading import Thread
import re

class Chatbot():
    def __init__(self) -> None:
        self.faiss_index = get_faiss_index()
        self.conversation= initialize_chat_conversation(self.faiss_index)
        
    def generate_response(self, query,  user_messages_history=""):
        query = translate_vi2en(query)
        self.conversation.run(input = query, user_messages_history=user_messages_history)

    # def generate_response_stream(self, query, user_messages_history=""):
    #     t = Thread(target=self.generate_response, kwargs={"query": query, "user_messages_history": user_messages_history})
    #     t.start()
    #     for new_text in self.streamer:
    #         yield new_text

    def get_response(self, query, user_messages_history=""):
        query = translate_vi2en(query)
        response = self.conversation.run(input = query, user_messages_history=user_messages_history)
        return response