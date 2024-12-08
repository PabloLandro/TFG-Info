import os, requests, re

from dotenv import load_dotenv

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
with open('resources/prompt_v2.txt', 'r') as file:
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

def evaluate(description, narrative, doc):    

    try:
        # Replace the fields in the template
        prompt = template.replace("%DESCRIPTION%", description).replace("%NARRATIVE%", narrative).replace("%DOCUMENT%",doc)

        # Add a message to the payload
        payload["messages"] = [{"role": "user", "content": prompt}]

        # Make a POST request to the API endpoint
        response = requests.post(api_url, headers=headers, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            response_content = response.json()['choices'][0]['message']['content']
            output_format = r'^(0|1|2) (0|1|2) (0|1|2)$'
            if not bool(re.match(output_format,response_content)):
                raise Exception(f"Error: Format of response invalid: {response_content}")
            out = {}
            out["u"], out["s"], out["cr"] = response_content.split()
            return out
        else:
            # Handle error responses
            raise Exception(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error in gpt.py: {e}")
