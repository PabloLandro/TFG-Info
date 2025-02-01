import os, requests, re, sys
import json

from openai import OpenAI

from dotenv import load_dotenv

import tiktoken

# Get api key from .env
load_dotenv()
api_key = os.getenv("API_KEY")

model="gpt-4o-mini"
max_tokens=150
api_url = "https://api.openai.com/v1/chat/completions"

# Set up headers including the authorization token
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Read the template prompt from file
template = ""
with open(os.path.join("resources", "prompts", "prompt_v2.txt"), 'r') as file:
    template = file.read()

# Define the payload parameters
payload = {
    "model": model,
    "max_tokens": max_tokens,
    "n": 1,
    "stop": None,
    "temperature": 0.7,
    "messages": None
}

def get_prompt(description, narrative, doc):
    return template.replace("%DESCRIPTION%", description).replace("%NARRATIVE%", narrative).replace("%DOCUMENT%",doc)

encoding = tiktoken.encoding_for_model(model)

total_tokens = 0

def print_total_tokens():
    global total_tokens
    print("Total tokens: ", total_tokens)

def fill_prompt(description, narrative, doc, prompt_template):
    return prompt_template.replace("%DESCRIPTION%", description).replace("%NARRATIVE%", narrative).replace("%DOCUMENT%",doc)


def evaluate(description, narrative, doc, prompt_template=template):    
    global total_tokens

    try:
        # Replace the fields in the template
        prompt = fill_prompt(description, narrative, doc, prompt_template)

        #total_tokens += len(encoding.encode(prompt))

        # Add a message to the payload
        payload["messages"] = [{"role": "user", "content": prompt}]

        # Make a POST request to the API endpoint
        response = requests.post(api_url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            response_content = response.json()['choices'][0]['message']['content']
            output_format = r'^U=(0|1|2) S=(0|1|2) C=(0|1|2)$'
            if not bool(re.match(output_format,response_content)):
                raise Exception(f"Error: Format of response invalid: {response_content}")
            matches = re.findall(r"(U|S|C)=(0|1|2)", response_content)
            out = {key.lower() if key != "C" else "cr": int(value) for key, value in matches}
            print(out)
            return out
        else:
            # Handle error responses
            raise Exception(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error in gpt.py: {e}")

batch_data = []

def evaluate_batch(description, narrative, doc, prompt_template, topic_id, doc_id, prompt_name):
    global batch_data
    prompt = fill_prompt(description, narrative, doc, prompt_template)
    aux = {}
    aux["custom_id"] = topic_id + "-" + doc_id + "-" + prompt_name
    aux["method"] = "POST"
    aux["url"] = "/v1/chat/completions"
    aux["body"] = payload.copy()
    aux["body"]["messages"] = [{"role": "user", "content": prompt}]
    batch_data.append(aux)

def write_jsonl():
    global batch_data
    print("Writing jsonl")
    #print(batch_data)
    with open("batchinput.jsonl", "w") as file:
        for request in batch_data:
            file.write(json.dumps(request) + "\n")

def write_partition():
    global batch_data
    half = len(batch_data) // 2
    list1 = batch_data[:half]
    list2 = batch_data[half:]

    # Write the first part to a JSONL file
    with open('batchinput1.jsonl', 'w') as f1:
        for item in list1:
            json.dump(item, f1)
            f1.write('\n')

    # Write the second part to a JSONL file
    with open('batchinput2.jsonl', 'w') as f2:
        for item in list2:
            json.dump(item, f2)
            f2.write('\n')
    ##client = OpenAI()
#batch_input_file
#
#def upload_file_to_batch():
    #global client
    #global batch_input_file
    #batch_input_file = client.files.create(
        #file=open("batchinput.jsonl", "rb"),
        #purpose="batch"
    #)
    #print(batch_input_file)
#
#def create_batch():
    #global client
    #global batch_input_file
#
    #batch_input_file_id = batch_input_file.id
    #batch_object = client.batches.create(
        #input_file_id=batch_input_file_id,
        #endpoint="/v1/chat/completions",
        #completion_window="24h",
        #metadata={
            #"description": "trec evaluation",
        #}
    #)
    #with open("batch_object.txt", "w") as file:
        #file.write(json.dumps(batch_object))
#
#def print_batch_status(id):
    #global client
    #print(client.batches.retrieve(id))
#
#def cancel_batch(id):
    #global client
    #client.batches.cancel(id)


