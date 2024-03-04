import streamlit as st
import random
import time
import json
from googletrans import Translator
translator = Translator()

# result = translator.translate('hello', src='en', dest='vi')
from chatbotv1 import Chatbot
st.title("IX Health - Assistant")
chatbot = Chatbot()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
with st.chat_message("assistant"):
    message_placeholder = st.empty()
    message_placeholder.markdown("Xin chào, tôi là IXheath assistant, bạn có thể học tôi bất kì câu hỏi nào liên quan đến sức khỏe!")
# Accept user input
if prompt := st.chat_input("Hỏi bất cứ thứ gì liên quan đến sức khỏe."):
    # Add user message to chat history
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with open("chat/chat_history.json", "w") as f:
        json.dump(st.session_state.messages, f, indent=4, ensure_ascii=False)
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    prompt = translator.translate(prompt, src='vi', dest='en').text
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner(""):
            message_placeholder = st.empty()
            full_response = ""
            # history = []
            # if len(st.session_state.messages)>1:
            #     history = st.session_state.messages[-2:]
            for chunk in chatbot.chat(prompt):
                full_response += chunk + " "
                if '\n' in chunk:
                    full_response_tmp = translator.translate(full_response, src='en', dest='vi').text
                    message_placeholder.markdown(full_response_tmp+ "▌")
                # message_placeholder.markdown(full_response )
            full_response_tmp = translator.translate(full_response, src='en', dest='vi').text
            message_placeholder.markdown(full_response_tmp)
    # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response_tmp})
