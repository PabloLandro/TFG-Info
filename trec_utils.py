import os, re, json, sys
import xml.etree.ElementTree as ET
from pyserini.search.lucene import LuceneSearcher
from dotenv import load_dotenv

load_dotenv()

QRELS = {
    2019: os.path.join("misinfo-resources-2019", "qrels", "qrels_raw"),
    2020: os.path.join("misinfo-resources-2020", "qrels", "misinfo-2020-qrels"),
    2021: os.path.join("misinfo-resources-2021", "qrels", "qrels-35topics.txt"),
    2022: os.path.join("misinfo-resources-2022", "qrels", "qrels.final.oct-19-2022"),
}
QRELS_GRADED_USEFULNESS = {
    2019: os.path.join("misinfo-resources-2019", "qrels", "qrels_raw"),                 # NOT ADDED!
    2020: os.path.join("misinfo-resources-2020", "qrels", "misinfo-2020-qrels"),        # NOT ADDED!
    2021: os.path.join("misinfo-resources-2021", "qrels", "2021-derived-qrels", "misinfo-qrels-graded.usefulness"),
    2022: os.path.join("misinfo-resources-2022", "qrels", "qrels.final.oct-19-2022"),   # NOT ADDED!
}
TOPICS = {
    2019: os.path.join("misinfo-resources-2019", "topics", "misinfo-2019-topics.xml"),
    2020: os.path.join("misinfo-resources-2020", "topics", "misinfo-2020-topics.xml"),
    2021: os.path.join("misinfo-resources-2021", "topics", "misinfo-2021-topics.xml"),
    2022: os.path.join("misinfo-resources-2022", "topics", "misinfo-2022-topics.xml"),
}
INDEX_NAME = {
    2019: "clueweb_rawtext2",
    2020: "CC-NEWS-TREC-misinfo-2020",
    2021: "C4",
    2022: "C4",
}

YEAR = 2021 # Default to 2021
SEARCHER = None

def init_searcher():
    global SEARCHER
    INDEXES_DIR = os.environ.get("INDEXES_DIR")
    if not INDEXES_DIR:
        SEARCHER = None
        return
    from pyserini.search.lucene import LuceneSearcher
    index_path = os.path.join(INDEXES_DIR, INDEX_NAME[YEAR])
    SEARCHER = LuceneSearcher(index_path)

def set_year(year):
    global YEAR
    if year not in [2019, 2020, 2021, 2022]:
        raise Exception("Incorrect year")
    YEAR = year
    init_searcher()

    
def get_year_data(with_graded_usefulness=False):
    qrels_file = QRELS[YEAR]
    topics_file = TOPICS[YEAR]
    qrels = {}
    if with_graded_usefulness:
        qrels1 = get_qrels_dict(qrels_file)
        qrels2 = get_qrels_dict(QRELS_GRADED_USEFULNESS[YEAR], skip_unuseful=False)
        qrels = merge_qrels(qrels1, qrels2)
    else:
        qrels = get_qrels_dict(qrels_file)
    topics = get_topics_dict(topics_file)
    return qrels,topics

# This is used only in 2021 for the confussion matrices
def get_stats():
    if YEAR != 2021:
        print("Error: get_stats() is only implemented for YEAR == 2021.")
        sys.exit(1)
    data = {
        "u": {
            "pos_vals": [1, 2],  # Example array of integers
            "name": "Usefulness"
        },
        "s": {
            "pos_vals": [1, 2],  # Example array of integers
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
    return (parts + [None] * n)[:n]

def read_line_from_qrel(line):
    # Define parsing functions for each year
    def parse_2019(line):
        topic_id,_,doc_id,u,s,cr = unpack_split(line.split(), n=6)
        aux = {"topic_id": topic_id, "doc_id": doc_id, "u": u, "s": s, "cr": cr}
        preprocess_run(aux)
        return aux

    def parse_2020(line):
        return None

    def parse_2021(line):
        topic_id,_,doc_id,u,s,cr = unpack_split(line.split())
        aux = {"topic_id": topic_id, "doc_id": doc_id, "u": u, "s": s, "cr": cr}
        preprocess_run(aux)
        return aux

    def parse_2022(line):
        topic_id,doc_id,u,s = unpack_split(line.split(), n=4)
        aux = {"topic_id": topic_id, "doc_id": doc_id, "u": u, "s": s, "cr": None}
        preprocess_run(aux)
        return aux

    # Map years to their corresponding parsers
    year_parsers = {
        2019: parse_2019,
        2020: parse_2020,
        2021: parse_2021,
        2022: parse_2022,
    }

    # Get the parser for the given year
    parser = year_parsers.get(YEAR)

    # Parse the line using the appropriate parser
    return parser(line)

def get_qrels_dict(qrels_file, skip_unuseful=True):
    qrels = {}
    with open(qrels_file, "r") as file:
        for line in file:
            doc_run = read_line_from_qrel(line)
            if doc_run["u"] <= 0 and skip_unuseful:
                continue
            if doc_run["topic_id"] not in qrels:
                qrels[doc_run["topic_id"]] = {}
            qrels[doc_run["topic_id"]][doc_run["doc_id"]] = doc_run
    return qrels

#qrels1 has priority, in case of conflict, the entry from qrels1 will be kept
def merge_qrels(qrels1, qrels2):
    for topic_id in qrels2:
        if topic_id not in qrels1:
            qrels1[topic_id] = qrels2[topic_id]
            continue
        for doc_id in qrels2[topic_id]:
            if doc_id in qrels1[topic_id]:
                continue
            qrels1[topic_id][doc_id] = qrels2[topic_id][doc_id]
    return qrels1

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

def read_gpt_output(gpt_line):
    if YEAR == 2019:
        output_format = r'^R=(0|1|2) E=(0|1|2|3) C=(0|1)$'
        matches = re.findall(r"(R|E|C)=(0|1|2|3)", gpt_line)
        if not bool(re.match(output_format, gpt_line)):
            # Try to extract the pattern from a larger paragraph
            search = re.search(r"R=(0|1|2) E=(0|1|2|3) C=(0|1)", gpt_line)
            if search:
                print("Warning: Extracted code from paragraph for 2019.")
                code = search.group(0)
                matches = re.findall(r"(R|E|C)=(0|1|2|3)", code)
            else:
                raise Exception(f"Error: Format of response invalid: {gpt_line}")
        out = {key.lower() if key != "C" else "cr": int(value) for key, value in matches}
        print(out)
        return out

    if YEAR == 2021:
        output_format = r'^U=(0|1|2) S=(0|1|2) C=(0|1|2)$'
        matches = re.findall(r"(U|S|C)=(-1|0|1|2)", gpt_line)
        if not bool(re.match(output_format, gpt_line)):
            # Try to extract the pattern from a larger paragraph
            search = re.search(r"U=(0|1|2) S=(0|1|2) C=(0|1|2)", gpt_line)
            if search:
                print("Warning: Extracted code from paragraph for 2021.")
                code = search.group(0)
                matches = re.findall(r"(U|S|C)=(-1|0|1|2)", code)
            else:
                raise Exception(f"Error: Format of response invalid: {gpt_line}")
        out = {key.lower() if key != "C" else "cr": int(value) for key, value in matches}
        print(out)
        return out
    
    if YEAR == 2022:
        output_format = r'^U=(0|1|2) A=(0|1|2)$'
        matches = re.findall(r"(U|A)=(0|1|2)", gpt_line)
        if not bool(re.match(output_format, gpt_line)):
            # Try to extract the pattern from a larger paragraph
            search = re.search(r"U=(0|1|2) A=(0|1|2)", gpt_line)
            if search:
                print("Warning: Extracted code from paragraph for 2022.")
                code = search.group(0)
                matches = re.findall(r"(U|A)=(0|1|2)", code)
            else:
                raise Exception(f"Error: Format of response invalid: {gpt_line}")
        out = {key.lower() if key != "C" else "cr": int(value) for key, value in matches}
        print(out)
        return out

def write_run_to_file(file, topic_id, doc_id, run):

    if YEAR == 2019:
        write = f'{topic_id} 0 {doc_id} {run["r"]} {run["e"]} {run["cr"]}\n'
        file.write(write)
        print(f"writing: {write}")
        return

    if YEAR == 2021:
        write = f'{topic_id} 0 {doc_id} {run["u"]} {run["s"]} {run["cr"]}\n'
        file.write(write)
        print(f"write{write}")
        return

    if YEAR == 2022:
        write = f'{topic_id} {doc_id} {run["u"]} {run["a"]}\n'
        file.write(f'{topic_id} {doc_id} {run["u"]} {run["a"]}\n')
        print(f"write{write}")
        return

NOT_FOUND_LIST = []

def get_doc_content(doc_id):
    global NOT_FOUND_LIST

    # If SEARCHER is None, we use the downloads
    if SEARCHER is None:
        doc_path = os.path.join("downloaded_docs", f"docs_{YEAR}", f"{doc_id}.txt")
        try:
            with open(doc_path, "r", encoding="utf-8") as f:
                return f.read()
        except:
            print(f"ERROR, doc not found in downloads: {doc_path}")
            NOT_FOUND_LIST.append(doc_id)
            return None
        
    # If SEARCHER is not None, we use the index
    use_id = doc_id     # In some cases that <> tag needs to be added
    if SEARCHER.doc(doc_id) is None:
        print("changing id")
        use_id = "<urn:uuid:" + doc_id + "git >"
    try:
        return json.loads(SEARCHER.doc(use_id).raw())["text"]
    except:
        if not SEARCHER.doc(use_id) is None:
            return SEARCHER.doc(use_id).raw() 
        print(f"ERROR, doc not found: {doc_id}")
        NOT_FOUND_LIST.append(doc_id)
        return None

def print_not_found_docs():
    global NOT_FOUND_LIST
    print("The following docs where not found in the indexes")
    print(NOT_FOUND_LIST)