from gpt import chatgpt_query
from pyserini.search import LuceneSearcher


print('hello')
searcher = LuceneSearcher('/mnt/beegfs/groups/irgroup/indexes/CC-NEWS-TREC-misinfo-2020')
doc = searcher.doc('en.noclean.c4-train.00005-of-07168.143426')
print(doc.raw())

print("Write your query")

prompt = input("> ")


print(chatgpt_query(prompt))
