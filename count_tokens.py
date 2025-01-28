import tiktoken
from pyserini.search.lucene import LuceneSearcher
from trec_utils import get_qrels_dict_all
import json

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")

qrels = get_qrels_dict_all()

model = "gpt-4o-mini"

encoding = tiktoken.encoding_for_model(model)

total = 0

TOPICS = ["101", "102", "103", "104", "105"]

for topic_id in TOPICS:
    for doc_id in qrels[topic_id]:
        doc = json.loads(searcher.doc(doc_id).raw())["text"]
        total += len(encoding.encode(doc))
print("Total tokens: ", total) 
