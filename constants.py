# Number of snippets that will be added to the prompt. Too many snippets and you risk both the prompt going over the
# token limit, and the model not being able to find the correct answer
prompt_number_snippets = 2
# GPT related constants
gpt_model_to_use = 'ixhealth-assistant/models'
gpt_max_tokens = 1000

# Number of past user messages that will be used to search relevant snippets
search_number_messages = 1

faiss_path = './faiss_index'
chunk_size = 300
chunk_overlap = 50

# Number of snippets to be retrieved by FAISS
number_snippets_to_retrieve = 2
