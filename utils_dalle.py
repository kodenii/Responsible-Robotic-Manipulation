import os
from openai import AzureOpenAI
import json
import base64
from PIL import Image
from io import BytesIO

DALLE_ENDPOINT_NAME = ""
DALLE_DEPLOYMENT_NAME = "DALLE-3"
DALLE_KEY = ""

Azure_Client_DALLE = AzureOpenAI(
    api_version="2024-05-01-preview",
    api_key=DALLE_KEY,
    azure_endpoint=f"https://{DALLE_ENDPOINT_NAME}.openai.azure.com/",
)

def base64_to_image(base64_string):
    try:
        image_data = base64.b64decode(base64_string)
        image_buffer = BytesIO(image_data)
        image = Image.open(image_buffer)
        return image
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def generate_image_from_prompt(prompt, model=DALLE_DEPLOYMENT_NAME, size="1024x1024", quality="standard", n=1):
    try:
        client = Azure_Client_DALLE

        result = client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
            response_format='b64_json'
        )

        image_base64 = json.loads(result.model_dump_json()).get('data', [{}])[0].get('b64_json')
        if image_base64:
            return image_base64
        else:
            print("No image data returned in the response.")
            return None

    except Exception as e:
        print(f"An error occurred while generating the image: {e}")
        return None
    
def render(p, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    prompt = "a modern photo of " + p + ", Realistic, Based on real-life scenarios"
    image_base64 = generate_image_from_prompt(prompt)
    
    file_name = p + ".png"
    img_path = os.path.join(folder_path, file_name).replace("。", ".")
    
    image = base64_to_image(image_base64)
    
    try:
        image.save(img_path)
        return img_path  # Return the image path if successful
    except AttributeError as e:
        print(f"Error while saving image at {img_path}: {e}")
        # Return None or a fallback path if saving fails
        return None