# agents.py
import os, json, csv
from dotenv import load_dotenv
from openai import OpenAI
import Domains.Results.LLMs.prompts as prompts 

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
temp, max_tok = 0.1, 500

def describe_structure(image_b64, html_json, css_json):
    content = [
        {"type":"text","text":prompts.ui_structure_prompt},
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{image_b64}"}},
        {"type":"text","text":json.dumps(html_json)},
        {"type":"text","text":json.dumps(css_json)},
    ]
    msgs = [
        {"role":"system","content":prompts.ui_structure_system_message},
        {"role":"user","content":content},
    ]
    resp = client.chat.completions.create(
        model="gpt-4.1-mini-2025-04-14", messages=msgs, temperature=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content

def describe_styling(image_b64, html_json, css_json):
    content = [
        {"type":"text","text":prompts.ui_styling_prompt},
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{image_b64}"}},
        {"type":"text","text":json.dumps(html_json)},
        {"type":"text","text":json.dumps(css_json)},
    ]
    msgs = [
        {"role":"system","content":prompts.ui_styling_system_message},
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
        {"role": "system", "content": prompts.ui_evaluator_system_message},
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
        {"type": "text", "text": prompts.ui_formulator_prompt},
        {"type": "text", "text": json.dumps(evaluation_json)},
    ]
    msgs = [
        {"role": "system", "content": prompts.ui_formulator_system_message},
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
        {"type":"text","text":prompts.uba_evaluator_prompt},
        {"type":"text","text":json.dumps(uba)},
    ]
    msgs = [
        {"role":"system","content":prompts.uba_evaluator_system_message},
        {"role":"user","content":content},
    ]
    resp = client.chat.completions.create(
        model="gpt-4.1-mini", messages=msgs, temperatuere=temp, max_tokens=max_tok
    )
    return resp.choices[0].message.content

def generate_chart_configs(observations: str, uba_json: str) -> str:
    user_prompt = prompts.uba_plotter_prompt \
        .replace("{OBS}", observations) \
        .replace("{UBA}", uba_json)

    msgs = [
        {"role": "system", "content": prompts.uba_plotter_system_message},
        {"role": "user",   "content": user_prompt},
    ]

    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=msgs,
        temperature=temp,
        max_tokens=max_tok,
    )
    return resp.choices[0].message.content.strip()

import re
import requests
from openai import OpenAI

def evaluate_web_metrics(page_id: int, jwt_token: str) -> str:
    import Domains.Results.LLMs.prompts as prompts

    # Step 1: Fetch the metrics
    url = f"http://127.0.0.1:8000/toolkit/web-metrics/business/?page_id={page_id}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    metrics = response.json()["fs metrics"]

    # Step 2: Clean and convert values
    def parse_value(val: str) -> float:
        val = val.replace(",", "").strip()
        if val.endswith("ms"):
            return float(val.replace("ms", "")) / 1000
        if val.endswith("s"):
            return float(val.replace("s", ""))
        return float(val)

    cleaned_metrics = {
        "FCP": parse_value(metrics.get("First Contentful Paint", "0 s")),
        "SI": parse_value(metrics.get("Speed Index", "0 s")),
        "LCP": parse_value(metrics.get("Largest Contentful Paint (LCP)", "0 s")),
        "TTI": parse_value(metrics.get("Time to Interactive", "0 s")),
        "TBT": parse_value(metrics.get("Total Blocking Time (TBT)", "0 ms")),
        "CLS": parse_value(metrics.get("Cumulative Layout Shift (CLS)", "0")),
    }

    # Step 3: Send to OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    content = [
        {"type": "text", "text": prompts.web_metrics_evaluator_prompt},
        {"type": "text", "text": json.dumps({
            "page_id": str(page_id),
            "web_metrics": cleaned_metrics
        })}
    ]
    messages = [
        {"role": "system", "content": prompts.web_metrics_evaluator_system_message},
        {"role": "user", "content": content}
    ]
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=700
    )
    return response.choices[0].message.content
