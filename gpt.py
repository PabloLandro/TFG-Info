import os
import requests

from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the GPT api key
api_key = os.getenv("API_KEY")

def chatgpt_query(prompt, model="gpt-3.5-turbo", max_tokens=150):
    """
    Function to query OpenAI's ChatGPT API.

    Parameters:
    - prompt (str): The input prompt for the ChatGPT model.
    - api_key (str): Your OpenAI API key.
    - model (str): The model to use. Default is "gpt-3.5-turbo".
    - max_tokens (int): The maximum number of tokens to generate. Default is 150.

    Returns:
    - response_content (str): The generated text by ChatGPT.
    """

    # Define the API endpoint
    api_url = "https://api.openai.com/v1/chat/completions"

    # Set up headers including the authorization token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Define the payload with the prompt and other parameters
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "n": 1,
        "stop": None,
        "temperature": 0.7
    }

    # Make a POST request to the API endpoint
    response = requests.post(api_url, headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        response_content = response.json()
        return response_content['choices'][0]['message']['content']
    else:
        # Handle error responses
        raise Exception(f"Error: {response.status_code} - {response.text}")

# Example usage
if __name__ == "__main__":
    api_key = "your-api-key-here"
    prompt = "Write a short poem about the sea."
    try:
        response = chatgpt_query(prompt, api_key)
        print("ChatGPT response:", response)
    except Exception as e:
        print("An error occurred:", e)