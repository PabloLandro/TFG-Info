import os
import requests
from dotenv import load_dotenv
import tiktoken
import ollama  # Import Ollama library

# Load API key from .env
load_dotenv()
api_key = os.getenv("API_KEY")

# Centralized configuration for models
MODEL_CONFIGS = {
    "gpt-4o-mini": {
        "api_url": "https://api.openai.com/v1/chat/completions",
        "encoding": tiktoken.encoding_for_model("gpt-4o-mini"),
        "library": "openai"
    },
    "llama3": {
        "api_url": None,  # Ollama doesn't use API URLs
        "encoding": None,  # Encoding not needed for Ollama
        "library": "llama3:8b-instruct-q4_1"
    }
}

# Default model
current_model = "gpt-4o-mini"
model_config = MODEL_CONFIGS[current_model]

# Update model and configurations
def set_model(model_name):
    global current_model, model_config
    if model_name not in MODEL_CONFIGS:
        raise ValueError(f"Model {model_name} not found. Available models: {list(MODEL_CONFIGS.keys())}")
    current_model = model_name
    model_config = MODEL_CONFIGS[model_name]

# Common evaluate function
def evaluate(query, description, narrative, doc, prompt_template, no_evaluate=True):
    global total_tokens

    # Replace the fields in the template
    prompt = fill_prompt(query, description, narrative, doc, prompt_template)

    if model_config["library"] == "openai":
        # OpenAI: Calculate tokens and make HTTP request
        encoding = model_config["encoding"]
        total_tokens += len(encoding.encode(prompt))

        if no_evaluate:
            return None

        # Prepare payload
        payload = {
            "model": current_model,
            "max_tokens": 150,
            "n": 1,
            "stop": None,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        }

        # Make OpenAI API request
        response = requests.post(model_config["api_url"], headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }, json=payload)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    elif model_config["library"] == "ollama":
        # Ollama: Directly call the chat function
        if no_evaluate:
            return None

        response = ollama.chat(model=current_model, messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ])
        return response['message']['content']

# Example: fill_prompt function
def fill_prompt(query, description, narrative, doc, prompt_template):
    return prompt_template.replace("%QUERY%", query).replace("%DESCRIPTION%", description).replace("%NARRATIVE%", narrative).replace("%DOCUMENT%", doc)
