from gpt import chatgpt_query

print("Write your query")

prompt = input("> ")

print(chatgpt_query(prompt))