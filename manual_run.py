
from dotenv import load_dotenv
import os, requests

load_dotenv()

#### Talk to grok model #######
def ask_model(message, tool=None):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    h = {'Content-Type': 'application/json', 
         'Authorization': 'Bearer ' + os.getenv("GROQ_API_KEY")}
    body = {'model': "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": message}]} 
    response = requests.post(url, headers = h, json = body)
    print(response.json())
    output = response.json()['choices'][0]['message']['content']
    return output

query = 'Explain theory of relativity in 5 sentences?'
response = ask_model(query)
print(response)
