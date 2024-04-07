RAG = """
    Give the answer to the user query delimited by triple backticks ```{query}```\
    using the information given in context delimited by triple backticks ```{context}```.\
    If there is no relevant information in the provided context, try to answer yourself, 
    but tell user that you did not have any relevant context to base your answer on.
    Be concise and output the answer of size less than 80 tokens.
"""