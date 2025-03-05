import os, requests, re


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


def evaluate(description, narrative, doc, prompt_template=template, no_evaluate=True):    
    global total_tokens

    try:
        # Replace the fields in the template
        prompt = fill_prompt(description, narrative, doc, prompt_template)

        total_tokens += len(encoding.encode(prompt))
        if no_evaluate:
            return None
        print("Sending request")

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