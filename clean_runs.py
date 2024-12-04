import os
from trec_utils import get_qrels_dict_all

qrels = get_qrels_dict_all()

for topic_id in os.listdir("runs"):
    count = 0
    with open(os.path.join("runs", topic_id), "r") as infile, open("aux", "w") as outfile:
        for line in infile:
            doc_id,_,_,_ = line.split()
            if doc_id in qrels[topic_id]:
                count += 1
                outfile.write(line)
    print(count)
    break

