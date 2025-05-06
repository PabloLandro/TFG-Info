import os
os.environ["INDEXES_PATH"] = "/mnt/beegfs/groups/irgroup/indexes"

from pyserini.search.lucene import LuceneSearcher
from trec_utils import set_year, get_year_data, get_doc_content, read_line_from_qrel

YEAR = 2019
RUNS_FILE=os.path.join("runs", f"runs_{YEAR}")
# Set year to 2021
set_year(YEAR)

# Get the searcher for 2021
_, _, searcher = get_year_data()

# Create output directory
output_dir = f"docs_{YEAR}"
os.makedirs(output_dir, exist_ok=True)

# Read document IDs from DesDelStr_2021
doc_ids = set()
with open(RUNS_FILE, "r") as f:
    for line in f:
        aux = read_line_from_qrel(line)
        doc_ids.add(aux["doc_id"])

# Download and save each document
for doc_id in doc_ids:
    try:
        # Get document content
        doc = get_doc_content(searcher, doc_id)
        if doc is not None:
            # Save document content to file
            output_file = os.path.join(output_dir, f"{doc_id}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(doc)
            print(f"Saved document {doc_id}")
        else:
            print(f"Document {doc_id} not found")
    except Exception as e:
        print(f"Error processing document {doc_id}: {str(e)}")

print(f"Downloaded {len(doc_ids)} documents to {output_dir}")
