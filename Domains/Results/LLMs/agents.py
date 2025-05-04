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
        {"type": "text", "text": prompts.ui_evaluator_prompt},
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
    # 1. Load the UBA file
    if uba_path.lower().endswith(".csv"):
        with open(uba_path, newline="", encoding="utf-8") as f:
            uba = list(csv.DictReader(f))
    else:
        with open(uba_path, "r", encoding="utf-8") as f:
            uba = json.load(f)

    # 2. Build LLM payload
    content = [
        {"type": "text", "text": prompts.uba_evaluate_prompt},
        {"type": "text", "text": json.dumps(uba)},
    ]
    messages = [
        {"role": "system", "content": prompts.uba_evaluate_system_message},
        {"role": "user", "content": content},
    ]

    # 3. Call the model
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
    )

    # 4. Extract the raw string (not the method!)
    report_str = resp.choices[0].message.content

    # 5. If it’s JSON, parse it; otherwise leave as string
    try:
        report = json.loads(report_str)
    except (json.JSONDecodeError, TypeError):
        report = report_str

    return report

def generate_chart_configs(observations: str, uba_json: str) -> str:
    user_prompt = prompts.uba_plotter_prompt \
        .replace("{OBS}", observations) \
        .replace("{UBA}", uba_json)

    msgs = [
        {"role": "system", "content": prompts.uba_plotter_system_message},
        {"role": "user",   "content": user_prompt},
    ]


def web_search_agent(problem: str) -> list[dict]:
    """
    Takes a single UBA 'problem' string.
    Returns a list of {source, summary} dicts.
    """
    resp = client.chat.completions.create(
        model="o3-mini-2025-01-31",          # browsing-enabled o-series model
        messages=[
            {"role": "system", "content": prompts.web_search_system_message},
            {"role": "user",   "content": problem}
        ],
        response_format={"type": "json_object"}   # ← forces pure JSON
    )
    # The model must reply with a JSON string; parse it.
    payload = json.loads(resp.choices[0].message.content)
    return payload.get("resources", [])


def evaluate_web_metrics(raw_metrics: dict) -> str:
    """
    1. Parse input metrics (strings like "1.2 s", "390 ms", etc.)
    2. Call OpenAI agent to evaluate.
    3. Return the LLM's JSON string.
    """
    def _parse(val: str) -> float:
        v = val.replace(",", "").strip()
        if v.endswith("ms"): return float(v[:-2]) / 1000
        if v.endswith("s"):  return float(v[:-1])
        return float(v)

    # Cleaned numeric metrics
    cleaned = { 
        # normalize key names to match prompt expectations:
        # e.g. "First Contentful Paint" -> "FCP"
        # feel free to adjust mapping if you renamed metrics
        {"First Contentful Paint": "FCP",
         "Speed Index":             "SI",
         "Largest Contentful Paint (LCP)": "LCP",
         "Time to Interactive":     "TTI",
         "Total Blocking Time (TBT)":  "TBT",
         "Cumulative Layout Shift (CLS)": "CLS"
        }[k]: _parse(v)
        for k, v in raw_metrics.items()
        if k in {
            "First Contentful Paint",
            "Speed Index",
            "Largest Contentful Paint (LCP)",
            "Time to Interactive",
            "Total Blocking Time (TBT)",
            "Cumulative Layout Shift (CLS)"
        }
    }

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [
        {"role": "system", "content": prompts.web_metrics_evaluator_system_message},
        {"role": "user",   "content": [
            {"type": "text", "text": prompts.web_metrics_evaluator_prompt},
            {"type": "text", "text": json.dumps({"web_metrics": cleaned})}
        ]}
    ]
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.2,
        max_tokens=700
    )
    return resp.choices[0].message.content
    
    # Convert Markdown links to HTML links to make them clickable in the response
    output_text = resp.output_text
    # Convert markdown links [text](url) to HTML links <a href="url">text</a>
    output_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', output_text)
    
    return output_text

