# agents.py
import os, json
from dotenv import load_dotenv
from openai import OpenAI
import Domains.Results.LLMs.prompts as prompts 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
temp, max_tok = 0.1, 500

def describe_structure(image_b64, html_json, css_json):
    content = [
        {"type":"text","text":prompts.structure_prompt},
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{image_b64}"}},
        {"type":"text","text":json.dumps(html_json)},
        {"type":"text","text":json.dumps(css_json)},
    ]
    msgs = [
        {"role":"system","content":prompts.structure_system_message},
        {"role":"user","content":content},
    ]
    resp = client.chat.completions.create(
        model="gpt-4.1-2025-04-14", messages=msgs, temperature=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content

def describe_styling(image_b64, html_json, css_json):
    content = [
        {"type":"text","text":prompts.styling_prompt},
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{image_b64}"}},
        {"type":"text","text":json.dumps(html_json)},
        {"type":"text","text":json.dumps(css_json)},
    ]
    msgs = [
        {"role":"system","content":prompts.styling_system_message},
        {"role":"user","content":content},
    ]
    resp = client.chat.completions.create(
        model="gpt-4o", messages=msgs, temperature=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content

import json
from openai import OpenAI
import Domains.Results.LLMs.prompts as prompts

def evaluate_ui(
    ui_report: dict,
    screenshot_b64: str,
    business_type: str,
    page_type: str
) -> str:

    content = [
        {"type": "text", "text": prompts.evaluate_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
        {"type": "text", "text": json.dumps(ui_report)},
        {"type": "text", "text": f"Business type: {business_type}"},
        {"type": "text", "text": f"Page type: {page_type}"},
    ]
    msgs = [
        {"role": "system", "content": prompts.evaluate_system_message},
        {"role": "user",   "content": content},
    ]

    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=msgs,
        temperature=temp,
        max_tokens=max_tok,
    )
    return resp.choices[0].message.content

def formulate_ui(evaluation_json: dict) -> str:
    content = [
        {"type": "text", "text": prompts.formulator_prompt},
        {"type": "text", "text": json.dumps(evaluation_json)},
    ]
    msgs = [
        {"role": "system", "content": prompts.formulator_system_message},
        {"role": "user",   "content": content},
    ]
    resp = client.chat.completions.create(
        model="gpt-4o", messages=msgs, temperature=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content
