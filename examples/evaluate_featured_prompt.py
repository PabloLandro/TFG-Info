import sys
import os
sys.path.append(os.getcwd())
from get_runs import copy_run_list_from_folder, get_prompt_template_list, get_run_list, run_run_list
from gpt import print_total_tokens, write_jsonl, write_partition


#TOPIC_LIST = os.listdir(os.path.join("runs", "runs_v1"))   # Topics to run
TOPIC_LIST = ["101"]            # Topics to run
PROMPT_NAME = "prompt_features_v1.txt"                      # Prompt file located in resources/prompts
OUTPUT_FOLDER = "runs_features_v1"                          # Folder located in runs/
EXCLUDE = True                                             # If we already have evaluated (topic_id, doc_id) pairs in the output folder that we don´t need to reevaluate, these can be skipped  
NUM_RUNS = 10e9                                             # Maximum number of (topic_id, doc_id) we want to evaluate


out_dir = os.path.join("runs", OUTPUT_FOLDER)

featured_prompt_template = ""
prompt_path = os.path.join("resources", "prompts", PROMPT_NAME)
with open(prompt_path, "r") as file:
    featured_prompt_template = file.read()

run_list = get_run_list(TOPIC_LIST) 
prompt_template_list = get_prompt_template_list(featured_prompt_template)

for (prompt_template, features) in prompt_template_list:
    folder_name = ""
    if len(features) == 0:
        folder_name = "Nothing"
    else:
        folder_name = "".join([feature[0].upper() + feature[1] + feature[2] for feature in features])
    if folder_name != "RolDelStr":
        continue
    print("Evaluating ] ", folder_name)
    path = os.path.join(out_dir, folder_name)
    os.makedirs(path, exist_ok=True)
    exclude_list = []
    if EXCLUDE:
        exclude_list = copy_run_list_from_folder(path)
    
    run_list = get_run_list(TOPIC_LIST, exclude_list = exclude_list)

    #print(f"Evaluating {folder_name} with prompt:\n{prompt_template}")

    run_run_list(prompt_template, run_list, num_runs=NUM_RUNS, directory=path, prompt_name=folder_name)
#write_jsonl()
#write_partition()
#print_total_tokens()
