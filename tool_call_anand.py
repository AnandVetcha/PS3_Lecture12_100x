
from dotenv import load_dotenv
import os, requests, json
import pandas as pd

load_dotenv()

SHEET_URL = 'https://docs.google.com/spreadsheets/d/1nNmMTIbEFn1xzN7S9_QHRyomYBSUc9sK1xab5WqjKOk/edit?gid=0#gid=0'

#### create tools ####################

def get_project_list(sheet_url = SHEET_URL):
    if sheet_url is None:
        sheet_url = SHEET_URL
    sheet_id = sheet_url.split('/d/')[1].split('/')[0]
    worksheet_index = sheet_url.split('gid=')[1].split('#')[0]
    df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
    return df['Project'].unique().tolist()

#### Talk to grok model #######
def ask_model(message, tool=None):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    h = {'Content-Type': 'application/json', 
         'Authorization': 'Bearer ' + os.getenv("GROQ_API_KEY")}
    body = {'model': "openai/gpt-oss-120b",
            "messages": message}
    if tool != None:
        body['tools'] = tool
    response = requests.post(url, headers = h, json = body)
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        if 'tool_calls' in response.json()['choices'][0]['message'].keys():
            results = []
            for tool_call in response.json()['choices'][0]['message']['tool_calls']:
                print("Tool call detected:", json.dumps(tool_call, indent=2, ensure_ascii=False))
                function_name = tool_call['function']['name']
                arguments = tool_call['function']['arguments']
                arguments = json.loads(arguments)
                print("Function name:", function_name)
                print("Arguments:", arguments)
                result = available_functions[function_name](**arguments)
                print("Result:", result)
                results.append(result)
                message.append({"role": "tool", 'tool_call_id': tool_call['id'], "content": json.dumps(result)})
            print('#####################')
            print(json.dumps(message, indent=2, ensure_ascii=False))
            return 1
        else:
            output = response.json()['choices'][0]['message']['content']
            return output
    else:
        return f"Error: {response.status_code} - {response.text}"   

##### available functions ##########
available_functions = {
    "get_project_list": get_project_list
}


########## INteraction with LLM ##################
query = 'At ACME which projects are we currently working on?'
messages = [{"role": "user", "content": query}]
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
                    "sheet_url" : {'type': ['string','null'], 'description': 'Optional Google SHeet URL. Omit to use the default URL of the ACME projects spreadsheet'}
                }
            }
        }
    }
]


response = ask_model(messages, tool=tool_card)
print(response)

#sheet_id = SHEET_URL.split('/d/')[1].split('/')[0]
#worksheet_index = SHEET_URL.split('gid=')[1].split('#')[0]
#df = pd.read_csv(f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={worksheet_index}')
#print(df.head())
#print(get_project_list(SHEET_URL))
