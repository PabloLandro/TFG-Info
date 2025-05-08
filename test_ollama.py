import ollama, os,sys
from trec_utils import set_year, get_year_data, get_doc_content, read_gpt_output, write_run_to_file
from gpt import fill_prompt
from llama3_tokenizer import get_tokenizer

set_year(2021)
qrels,topics = get_year_data()

doc_id = None
count = 1

prompt_template = ""
with open(os.path.join("resources", "prompts", "DesDelStr_2021.txt"), "r") as file:
    prompt_template = file.read()

tokenizer = get_tokenizer("llama3-8b-instruct-q4_1")

tokens = tokenizer.encode(prompt_template, return_tensors="pt")  # Use 'return_tensors' for PyTorch tensors

# Tokens contain input_ids, attention_mask, etc.
print(tokens)
sys.exit(0)
with open(os.path.join("runs", "DesDelStr_2021_llama3"), "a") as out_file:
    for id in qrels["101"].keys():
        if count <= 17:
            count = count +1
            continue
        doc_id = id
        doc = get_doc_content(doc_id)
        

        prompt = fill_prompt(topics["101"]["query"], topics["101"]["description"], topics["101"]["narrative"], doc, prompt_template)

        print(prompt)

        model_name = "llama3:8b-instruct-q4_1"

        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        llama_output = response["message"]["content"]
        print("Response from Ollama:")
        print(llama_output)
        if llama_output is None:
            continue
        try:
            run = read_gpt_output(llama_output)
        except:
            continue
        if run is None:
            raise Exception("None run")
        write_run_to_file(out_file, 101, doc_id, run)
