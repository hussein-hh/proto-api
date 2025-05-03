# agents.py
import os, json, csv
from dotenv import load_dotenv
from openai import OpenAI
import Domains.Results.LLMs.prompts as prompts 
import re  # Add import for regex

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
        model="gpt-4.1-mini-2025-04-14", messages=msgs, temperature=temp, max_tokens=max_tok
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
        model="gpt-4.1-mini", messages=msgs, temperature=temp, max_tokens=max_tok
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
        {"type": "text", "text": prompts.evaluator_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
        {"type": "text", "text": json.dumps(ui_report)},
        {"type": "text", "text": f"Business type: {business_type}"},
        {"type": "text", "text": f"Page type: {page_type}"},
    ]
    msgs = [
        {"role": "system", "content": prompts.evaluator_system_message},
        {"role": "user",   "content": content},
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
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
        model="gpt-4.1-mini", messages=msgs, temperature=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content


def evaluate_uba(uba_path):
    # load UBA as JSON or CSV
    if uba_path.lower().endswith(".csv"):
        with open(uba_path, newline="", encoding="utf-8") as f:
            uba = list(csv.DictReader(f))
    else:
        uba = json.load(open(uba_path, "r", encoding="utf-8"))

    # build your LLM payload exactly as before
    content = [
        {"type":"text","text":prompts.uba_evaluate_prompt},
        {"type":"text","text":json.dumps(uba)},
    ]
    msgs = [
        {"role":"system","content":prompts.uba_evaluate_system_message},
        {"role":"user","content":content},
    ]
    resp = client.chat.completions.create(
        model="o3-mini-2025-01-31", messages=msgs, #temperature=temp, #max_tokens=max_tok
    )
    return resp.choices[0].message.content



def web_search_agent(problem: str) -> str:
    """
    Use GPT-4o-mini with the web_search tool to find solutions for the given problem.
    Returns a concise answer with source citations.
    """
    
    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions=prompts.web_search_system_message,
        input=prompts.web_search_prompt.format(query=problem),
        tools=[{"type": "web_search"}]
    )
    
    # Convert Markdown links to HTML links to make them clickable in the response
    output_text = resp.output_text
    # Convert markdown links [text](url) to HTML links <a href="url">text</a>
    output_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', output_text)
    
    return output_text

def webby_search_agent(query: str) -> str:
    """
    Uses GPT-4o-mini plus the web_search tool to answer any internet query.
    Returns HTML-ified output with <a> links.
    """
    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions=prompts.WEBBY_SEARCH_SYSTEM_MESSAGE,
        input=prompts.WEBBY_SEARCH_PROMPT.format(query=query.strip()),
        tools=[{"type": "web_search"}],
        # temperature=0.2,
        # max_tokens=700,
    )

    # convert Markdown links to HTML links
    output = resp.output_text or ""
    return re.sub(
        r'\[([^\]]+)\]\(([^)]+)\)',
        r'<a href="\2" target="_blank">\1</a>',
        output
    ).strip()
