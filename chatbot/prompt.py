from langchain_core.prompts.prompt import PromptTemplate
prompt = """The following is a friendly conversation between a customer and you. Please answer the customer's needs based on the provided documents and the conversation history.
Chat history :
{chat_history}
The answer must include important main ideas and focus on the heart of the question. For questions that require inference, provide detailed and easy-to-understand explanations for users
Customer: {question}
Think steps by step to make your answer clear and easy to understand.
Your response: 
"""


prompt_with_context = """The following document can be used to help you answer the questions:    
{context}    
The following is a conversation between a customer and you. Please answer the customer's needs based on the provided documents and the conversation history.
Chat history :
{chat_history}

The answer must include important main ideas and focus on the heart of the question. For quantity questions (like asking about the calories in chicken) you only need to give the amount in 1 kg
Customer: {question}
You must write the most important points you found in the content to make your answer easier to read!
You don't need to speak "Based on the provided information" or "According to the document". Just answer the question directly.
Think steps by step to make your answer clear and easy to understand.
Your response: 
"""

PROMPT = PromptTemplate.from_template(prompt)
PROMPT_WITH_CONTEXT = PromptTemplate.from_template(prompt_with_context)
