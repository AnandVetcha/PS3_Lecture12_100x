
from dotenv import load_dotenv
import os, requests
import pandas as pd

load_dotenv()

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1nNmMTIbEFn1xzN7S9_QHRyomYBSUc9sK1xab5WqjKOk/edit?gid=0#gid=0'


#### create tools ####################

def get_project_list(SHEET_URL):
    sheet_id = SHEET_URL.split('/d/')[1].split('/')[0]
    worksheet_index = SHEET_URL.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return df['Project'].unique()

#### Talk to grok model #######
def ask_model(message, tool=None):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    h = {'Content-Type': 'application/json', 
         'Authorization': 'Bearer ' + os.getenv("GROQ_API_KEY")}
    body = {'model': "openai/gpt-oss-120b",
            "messages": [{"role": "user", "content": message}]}
    if tool != None:
        body['tools'] = tool
    response = requests.post(url, headers = h, json = body)
    if response.status_code == 200:
        output = response.json()['choices'][0]['message']['content']
        return output
    else:
        return f"Error: {response.status_code} - {response.text}"   


########## INteraction with LLM ##################
query = 'At ACME which projects are we currently working on?'

###### Create tool card ########
tool_card = [
    {
        "type" : "function",
        "function" : 
        {
            "name": "get_project_list",
            "description": "Get the list of current working projects at ACME",
            "parameters": 
            {
                "type": "object",
                "properties" : 
                {
                    "SHEET_URL" : {'type': 'string', 'description': 'URL of the ACME projects spreadsheet'}
                }
            }
        }
    }
]


response = ask_model(query, tool=tool_card)
print(response)

#sheet_id = SHEET_URL.split('/d/')[1].split('/')[0]
#worksheet_index = SHEET_URL.split('gid=')[1].split('#')[0]
#df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
#print(df.head())
#print(get_project_list(SHEET_URL))
