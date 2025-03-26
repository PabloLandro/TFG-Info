import os, requests

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

# Define the payload parameters
payload = {
    "model": model,
    "max_tokens": max_tokens,
    "n": 1,
    "stop": None,
    "temperature": 0.7,
    "messages": None
}

encoding = tiktoken.encoding_for_model(model)

total_tokens = 0

def print_total_tokens():
    global total_tokens
    print("Total tokens: ", total_tokens)

def fill_prompt(query, description, narrative, doc, prompt_template):
    return prompt_template.replace("%QUERY%", query).replace("%DESCRIPTION%", description).replace("%NARRATIVE%", narrative).replace("%DOCUMENT%",doc)


def evaluate(query, description, narrative, doc, prompt_template, no_evaluate=True):    
    global total_tokens

    # Replace the fields in the template
    prompt = fill_prompt(query, description, narrative, doc, prompt_template)
    if total_tokens == 0:
        print(prompt)
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
        print(response_content)
        return response_content
    else:
        # Handle error responses
        raise Exception(f"Error: {response.status_code} - {response.text}")
