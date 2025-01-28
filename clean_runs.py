import os
from trec_utils import get_qrels_dict_all

# This script removes any runs from FOLDER that are not present in any qrel

FOLDER = "runs"

qrels = get_qrels_dict_all()

for topic_id in os.listdir(FOLDER):
    with open(os.path.join(FOLDER, topic_id), "r") as infile, open("aux", "w") as outfile:
        for line in infile:
            doc_id,_,_,_ = line.split()
            if doc_id in qrels[topic_id]:
                outfile.write(line)
    os.replace("aux", os.path.join(FOLDER, topic_id))
