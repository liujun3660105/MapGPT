# RAG = """
#     Give the answer to the user query delimited by triple backticks ```{query}```\
#     using the information given in context delimited by triple backticks ```{context}```.\
#     If there is no relevant information in the provided context, try to answer yourself, 
#     but tell user that you did not have any relevant context to base your answer on.
#     Be concise and output the answer of size less than 80 tokens.
# """
RAG = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context and the chatHistory to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Question: {query}
chatHistory:{chatHistory} 
Context: {context} 
Answer:

"""
