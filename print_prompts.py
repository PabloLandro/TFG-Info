from gpt import get_prompt
from pyserini.search.lucene import LuceneSearcher
import json
from trec_utils import get_topics_dict
from tqdm import tqdm
import os

FILE = "aux.txt"

searcher = LuceneSearcher("/mnt/beegfs/groups/irgroup/indexes/C4/")
topics = get_topics_dict("misinfo-2021-topics.xml")

total_lines = sum(1 for _ in open(FILE, "r"))

with open(FILE, "r") as file:
    iterator = tqdm(file, total=total_lines, desc=f"Creating prompts from {FILE}", unit=" prompts")
    for line in iterator:
        topic_id,doc_id = line.split()
        with open(os.path.join("FP_prompts", f"{topic_id},{doc_id}"), "w") as out:
            doc = json.loads(searcher.doc(doc_id).raw())["text"]
            out.write(get_prompt(topics[topic_id]["description"], topics[topic_id]["narrative"], doc))
