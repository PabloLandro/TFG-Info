import os
from trec_utils import get_qrels_dict

for name in os.listdir(os.path.join("resources", "qrels")):
    print(name)
    qrels = get_qrels_dict(name)
    for topic_id in qrels:
        pos = 0
        neg = 0
        for doc_id in qrels[topic_id]:
            if qrels[topic_id][doc_id]['u'] > 0:
                pos += 1
            else:
                neg += 1
        print(f"{topic_id} {pos} {neg}")
    
