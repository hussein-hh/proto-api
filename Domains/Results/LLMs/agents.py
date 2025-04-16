import os
from dotenv import load_dotenv
from openai import OpenAI
from Domains.Results.LLMs.prompts import image_caption_system_message, image_caption_prompt

load_dotenv()

openai_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
temperature = 0.1
max_tokens = 500

def generate_caption(base64_image: str) -> str:

    messages = [
        {
            "role": "system",
            "content": image_caption_system_message
        },
        {
            "role": "user",
            "content": [
                {"type": "text", "text": image_caption_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]
        }
    ]
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    caption = response.choices[0].message.content
    return caption
