import streamlit as st
import os
from constants import search_number_messages
from langchain_utils import initialize_chat_conversation
from search_indexing import download_and_index_pdf, get_faiss_index
from googletrans import Translator
translator = Translator()
import re


def remove_url(url_to_remove):
    """
    Remove URLs from the session_state. Triggered by the respective button
    """
    if url_to_remove in st.session_state.urls:
        st.session_state.urls.remove(url_to_remove)
@st.cache_data
def save_file_locally(file):
    '''Save uploaded files locally'''
    doc_path = os.path.join('documents',file.name)
    # print(doc_path)
    with open(doc_path,'wb') as f:
        f.write(file.getbuffer())
    return doc_path
def delete_file_locally(file):
    '''Save uploaded files locally'''

    # print(doc_path)
    if os.path.exists(file):
        os.remove(file)
    # return doc_path

# Page title
st.set_page_config(page_title='IXHeath Assistant')
st.title('IXHeath Assistant - (Beta)')

# Initialize the faiss_index key in the session state. This can be used to avoid having to download and embed the same PDF
# every time the user asks a question
if 'faiss_index' not in st.session_state:
    st.session_state['faiss_index'] = {
        'indexed_urls': [],
        'index': None
    }

# Initialize conversation memory used by Langchain
if 'conversation_memory' not in st.session_state:
    st.session_state['conversation_memory'] = None

# Initialize chat history used by StreamLit (for display purposes)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store the URLs added by the user in the UI
if 'urls' not in st.session_state:
    st.session_state.urls = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
st.session_state['faiss_index']['index'] = get_faiss_index()
faiss_index = st.session_state['faiss_index']['index']
if st.session_state['conversation_memory'] is None:
    conversation = initialize_chat_conversation(faiss_index)
    st.session_state['conversation_memory'] = conversation
else:
    conversation = st.session_state['conversation_memory']
    
if query_text := st.chat_input("Your message"):

    # Display user message in chat message container, and append to session state
    st.chat_message("user").markdown(query_text)
    st.session_state.messages.append({"role": "user", "content": query_text})


    # Search PDF snippets using the last few user messages
    user_messages_history = [message['content'] for message in st.session_state.messages[-search_number_messages:] if message['role'] == 'user']
    user_messages_history = '\n'.join(user_messages_history)

    with st.spinner('Please wait..'):
        response = conversation.predict(input=translator.translate(query_text, src='vi', dest='en').text, user_messages_history=user_messages_history)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        vi_response = translator.translate(response, src='en', dest='vi').text
        st.markdown(vi_response)
        snippet_memory = conversation.memory.memories[1]
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": vi_response})
