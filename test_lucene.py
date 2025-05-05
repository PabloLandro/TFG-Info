from pyserini.search.lucene import LuceneSearcher
from get_runs import get_doc_content
import os, json

searcher1 = LuceneSearcher(os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "clueweb-b13"))
searcher2 = LuceneSearcher(os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "clueweb_rawtext2"))
searcher2022 = LuceneSearcher(os.path.join("/", "mnt", "beegfs", "groups", "irgroup", "indexes", "C4"))

#print(searcher1.doc("clueweb12-0606wb-65-21093") is None)
#print(searcher1.doc("clueweb12-0700tw-53-10819") is None)
#print(searcher1.doc("clueweb12-0700tw-81-13452") is None)
#print("doc en.noclean.c4-train.05287-of-07168.1336")
#print("official qrel: 1 0")
#print("LLM qrel: 1 2") 
#print(get_doc_content(searcher2022, "en.noclean.c4-train.05287-of-07168.1336"))
#print(get_doc_content(searcher2022, "en.noclean.c4-train.05576-of-07168.117496"))
#print(get_doc_content(searcher2022, "en.noclean.c4-train.06937-of-07168.25804"))


print("doc en.noclean.c4-train.00011-of-07168.21494")
print(get_doc_content(searcher2022, "en.noclean.c4-train.00011-of-07168.21494"))
