import os, sys
import xml.etree.ElementTree as ET
from pyserini.search.lucene import LuceneSearcher

QRELS_2019=os.path.join("misinfo-resources-2019", "qrels", "qrels_raw")
QRELS_2020=os.path.join("misinfo-resources-2020", "qrels", "misinfo-2020-qrels")
QRELS_2021=os.path.join("misinfo-resources-2021", "qrels", "qrels-35topics.txt")
QRELS_2022=os.path.join("misinfo-resources-2022", "qrels", "qrels.final.oct-19-2022")

TOPICS_2019=os.path.join("misinfo-resources-2019", "topics", "misinfo-2019-topics.xml")
TOPICS_2020=os.path.join("misinfo-resources-2020", "topics", "misinfo-2020-topics.xml")
TOPICS_2021=os.path.join("misinfo-resources-2021", "topics", "misinfo-2021-topics.xml")
TOPICS_2022=os.path.join("misinfo-resources-2022", "topics", "misinfo-2022-topics.xml")

#INDEX_2019=os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "clueweb-b13")
INDEX_2019=os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "clueweb_rawtext2")
INDEX_2020=os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "CC-NEWS-TREC-misinfo-2020")
INDEX_2021=os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "C4")
INDEX_2022=os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "C4")

def get_year_aux(year):
    if year == 2019:
        return QRELS_2019, TOPICS_2019, INDEX_2019
    if year == 2020:
        return QRELS_2020, TOPICS_2020, INDEX_2020
    if year == 2021:
        return QRELS_2021, TOPICS_2021, INDEX_2021
    if year == 2022:
        return QRELS_2022, TOPICS_2022, INDEX_2022
    print(f"ERROR, incorrect year {year}")
    sys.exit()

def get_year_data(year):
    qrels_file, topics_file, index_dir = get_year_aux(year)
    qrels = get_qrels_dict(qrels_file)
    topics = get_topics_dict(topics_file)
    searcher = LuceneSearcher(index_dir)
    return qrels,topics,searcher

def get_stats():
    data = {
        "u": {
            "pos_vals": [1, 2],  # Example array of integers
            "name": "Usefulness"
        },
        "s": {
            "pos_vals": [2],  # Example array of integers
            "name": "Supportiveness"
        },
        "cr": {
            "pos_vals": [1, 2],  # Example array of integers
            "name": "Credibility"
        }
    }
    return data


def preprocess_run(run):
    run["u"] = int(run["u"]) if run["u"] is not None else None
    run["s"] = int(run["s"]) if run["s"] is not None else None
    run["cr"] = int(run["cr"]) if run["cr"] is not None else None

def merge_doc_runs(doc_run1, doc_run2):
    out = {}
    error = False
    for id in doc_run1:
        if doc_run1[id] is None:
            out[id] = doc_run2[id]
        elif doc_run2[id] is None:
            out[id] = doc_run1[id]
        else:
            out[id] = doc_run1[id]
            if doc_run1[id] != doc_run2[id]:
                error = True

    return out, error


# Hay veces que un qrel o un run no tenga alguna de las etiquetas, en ese caso añadimos Nones
# para lo que tenemos que crear una función que lo handlee

def unpack_split(parts, n=6):
    return (parts + [None] * 6)[:6]

def read_line_from_qrel(line, year):
    # Define parsing functions for each year
    def parse_2019(line):
        return None

    def parse_2020(line):
        return None

    def parse_2021(line):
        topic_id,_,doc_id,u,s,cr = unpack_split(line.split())
        aux = {"topic_id": topic_id, "doc_id": doc_id, "u": u, "s": s, "cr": cr}
        preprocess_run(aux)
        return aux

    def parse_2022(line):
        return None

    # Map years to their corresponding parsers
    year_parsers = {
        2019: parse_2019,
        2020: parse_2020,
        2021: parse_2021,
        2022: parse_2022,
    }

    # Get the parser for the given year
    parser = year_parsers.get(year)
    if parser is None:
        raise ValueError(f"Unsupported year format: {year}")

    # Parse the line using the appropriate parser
    return parser(line)

def get_qrels_dict(qrels_file, skip_unuseful=True):
    qrels = {}
    with open(qrels_file, "r") as file:
        last_topic_id = ""
        run = {}
        for line in file:
            doc_run = {}
            doc_run["topic_id"], check, doc_run["doc_id"], doc_run["u"], doc_run["s"], doc_run["cr"] = unpack_split(line.split())

            # 2022 qrels dont have 0 separator
            if not check == "0":
                doc_run["s"] = doc_run["u"]
                doc_run["u"] = doc_run["doc_id"]
                doc_run["doc_id"] = check
                doc_run["cr"] = None

            preprocess_run(doc_run)
            if doc_run["u"] <= 0 and skip_unuseful:
                continue
            if last_topic_id != doc_run["topic_id"]:
                qrels[last_topic_id] = run
                last_topic_id = doc_run["topic_id"]
                run = {}
            run[doc_run["doc_id"]] = doc_run
    return qrels

def get_qrels_dict_all():
    qrels = {}

    for qrel_file_name in os.listdir(os.path.join("resources", "qrels")):
        qrels_file = os.path.join("resources", "qrels", qrel_file_name)
        aux = get_qrels_dict(qrels_file)
        for topic_id, topic_run in aux.items():
            # If that topic id isnt on our dict, we add it
            if topic_id not in qrels:
                qrels[topic_id] = topic_run
            # In other case we iterate over doc_ids to merge the topic_runs
            else:
                for doc_id, doc_run in aux[topic_id].items():
                    qrels[topic_id][doc_id], error = merge_doc_runs(qrels[topic_id][doc_id], doc_run)
                    if error:
                        print(f"ERROR: pair ({topic_id},{doc_id}) is in more than one qrel file")
    return qrels

def get_topics_dict(topics_file):
    # Open the topics file as an xml tree
    root = ET.parse(topics_file).getroot()
    
    # Load the topic into a dictionary
    topics = {}

    for topic in root.findall("topic"):

        topic_id = topic.find("number").text
        topics[topic_id] = {}

        # 2020 doesnt have query
        if not topic.find("query") is None:
            topics[topic_id]["query"] = topic.find("query").text
        else:
            topics[topic_id]["query"] = topic.find("title").text

        # 2022 doesnt have description
        if not topic.find("description") is None:
            topics[topic_id]["description"] = topic.find("description").text
        else:
            topics[topic_id]["description"] = topic.find("question").text

        # 2022 doesnt have narrative
        if not topic.find("narrative") is None:
            topics[topic_id]["narrative"] = topic.find("narrative").text
        else:
            topics[topic_id]["narrative"] = topic.find("background").text

    return topics
