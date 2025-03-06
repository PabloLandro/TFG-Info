import os
from trec_utils import get_qrels_dict_all

# This script removes any duplicate runs or runs from FOLDER that are not present in any qrel

FOLDER = "runs/runs_features_v1"

qrels = get_qrels_dict_all()


for name in os.listdir(FOLDER):
    for topic_id in os.listdir(os.path.join(FOLDER,name)):
        visited = []
        with open(os.path.join(FOLDER, name, topic_id), "r") as infile, open("aux", "w") as outfile:
            for line in infile:
                doc_id,_,_,_ = line.split()
                if doc_id in qrels[topic_id] and doc_id not in visited:
                    outfile.write(line)
                visited.append(doc_id)
        os.replace("aux", os.path.join(FOLDER, name, topic_id)) 
