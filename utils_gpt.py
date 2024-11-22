import requests
import base64
from io import BytesIO
from PIL import Image

GPT_ENDPOINT_NAME = ""
GPT_DEPLOYMENT_NAME = "gpt-4o"
GPT_KEY = ""

Azure_Config_GPT = {
    "agent_type": "Azure",
    "key": GPT_KEY,
    "endpoint": f"https://{GPT_ENDPOINT_NAME}.openai.azure.com/openai/deployments/{GPT_DEPLOYMENT_NAME}/chat/completions?api-version=2023-07-01-preview",
}

def img2b64(img: Image):
    buffered = BytesIO()
    # convert to jpeg
    img = img.convert('RGB')
    img.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    encoded = base64.b64encode(img_bytes).decode('ascii')
    return encoded

def submit(messages, agent_type: str, endpoint: str, key: str, temperature=0.7, top_p=0.95, max_tokens=800):
    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens
    }
    
    if agent_type == "Azure":
        headers.update({"api-key": key,})
    elif agent_type == "OpenAI":
        headers.update({"Authorization": f"Bearer {key}"})
        payload.update({"model": "gpt-4-vision-preview",})
    else:
        raise ValueError(f"Unknown agent type {agent_type}")
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json()
        response = results["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    return response

def get_messages(instruct: str, text: str=None, image: Image=None, history=[]):
    messages = [
          {
            "role": "system",
            "content": [
              {
                "type": "text",
                "text": instruct
              }
            ]
          }
    ]
    user_input = get_turn_user(text=text, image=image)
    for idx, msg in enumerate(history + [user_input]):
        if idx % 2 == 0:
            role = "user"
        else:
            role = "assistant"
        text = msg["text"] if "text" in msg else None
        image = msg["image"] if "image" in msg else None
        content = []
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        if image:
            encoded_image = img2b64(image)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                }
            })
        messages.append({
            "role": role,
            "content": content,
    })
    return messages

def get_turn_user(text: str=None, image: Image=None):
    user_input = {}
    if text:
        user_input.update({"text": text})
    if image:
        user_input.update({"image": image})
    return user_input

def get_turn_assistant(response: str=None):
    assistant_output = {}
    if response:
        assistant_output.update({"text": response})
    return assistant_output

class Agent(object):
    def __init__(self, agent_type: str, key: str, endpoint: str, instruct: str):
        self.key = key
        self.endpoint = endpoint
        self.instruct = instruct
        self.agent_type = agent_type
        self.history = []

    def chat(self, text: str=None, image: Image=None, add_history=False, use_history=False):
        history = self.history if use_history else []
        messages = get_messages(self.instruct, text, image, history)
        response = submit(messages, self.agent_type, self.endpoint, self.key)
        if add_history:
            self.add_turn(text=text, image=image, response=response)
        return response
    
    def add_turn(self, text: str=None, image: Image=None, response: str=None):
        user_input = get_turn_user(text=text, image=image)
        assistant_output = get_turn_assistant(response=response)
        self.history.append(user_input)
        self.history.append(assistant_output)
    
    @classmethod
    def from_config(cls, config, instruct: str):
        return cls(
            agent_type=config["agent_type"],
            key=config["key"],
            endpoint=config["endpoint"],
            instruct=instruct,
        )