# agents.py
import os, json, csv
from dotenv import load_dotenv
from openai import OpenAI
import Domains.Results.LLMs.prompts as prompts 
import re 
import Domains.Results.LLMs.criteria as criteria
import logging, time, json
from openai import RateLimitError

log = logging.getLogger("ux_eval")

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


# def evaluate_ui(
#     ui_report: dict,
#     screenshot_b64: str,
#     business_type: str,
#     page_type: str
# ) -> str:

#     content = [
#         {"type": "text", "text": prompts.ui_evaluator_prompt},
#         {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
#         {"type": "text", "text": json.dumps(ui_report)},
#         {"type": "text", "text": f"Business type: {business_type}"},
#         {"type": "text", "text": f"Page type: {page_type}"},
#     ]
#     msgs = [
#         {"role": "system", "content": prompts.ui_evaluator_system_message},
#         {"role": "user",   "content": content},
#     ]

#     resp = client.chat.completions.create(
#         model="gpt-4.1-mini",
#         messages=msgs,
#         temperature=temp,
#         max_tokens=max_tok,
#     )
#     return resp.choices[0].message.content

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


def web_search_agent(problem: str) -> list[dict]:
    """
    Takes a single UBA 'problem' string and returns
    a list of {source, summary} dicts using OpenAI’s
    search-preview model for live web results.
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini-search-preview",   # built-in web-search model
        messages=[
            {"role": "system",  "content": prompts.web_search_system_message},
            {"role": "user",    "content": problem}
        ]
        # Note: no response_format parameter here
    )

    # The assistant content is already JSON matching your schema
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


def uba_formulator(raw_report):
    """
    Transform a UBA report into plain‐language summaries as JSON.
    """
    report_str = raw_report if isinstance(raw_report, str) else json.dumps(raw_report)
    messages = [
        {"role": "system",  "content": prompts.uba_formulator_system_message},
        {"role": "user",    "content": prompts.uba_formulator_prompt + report_str},
    ]

    resp = client.chat.completions.create(
        model="o3-mini-2025-01-31",
        messages=messages,
    )
    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)   # <-- parse JSON here
    except json.JSONDecodeError:
        raise ValueError(f"LLM didn’t return valid JSON:\n{content}")

def evaluate_ui(ui_report, screenshot_b64, business_type, page_type):
    system_msg = prompts.build_ui_evaluator_system_message(page_type)

    content = [
        {"type": "text", "text": prompts.ui_evaluator_prompt},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
        {"type": "text", "text": json.dumps(ui_report)},
        {"type": "text", "text": f"Business type: {business_type}"},
        {"type": "text", "text": f"Page type: {page_type}"},
    ]

    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": system_msg},
                      {"role": "assistant", "content": json.dumps({
                          k: v["summary"]
                          for k, v in criteria.CRITERIA_BY_PAGE_TYPE[page_type].items()
                      })},
                      {"role": "user", "content": content}],
            temperature=temp,
            max_tokens=max_tok,
        )
    except RateLimitError as e:
        log.error(f"{page_type} | rate-limit: {e}")
        raise

    latency = time.time() - t0
    usage   = resp.usage  # if the SDK exposes token counts
    log.info(f"{page_type} | ok | {latency:.2f}s | prompt={usage.prompt_tokens} "
             f"→ completion={usage.completion_tokens}")

    raw = resp.choices[0].message.content
    result = json.loads(raw)

    GLOBAL_KEYS = criteria.CRITERIA_BY_PAGE_TYPE["global"].keys()
    expected = set(GLOBAL_KEYS) | set(criteria.CRITERIA_BY_PAGE_TYPE[page_type].keys())
    found    = {c["name"] for c in result.get("categories", [])}
    if expected != found:
        missing = expected - found
        extra   = found - expected
        log.warning(f"{page_type} | bad categories | missing={missing} extra={extra}")
        raise ValueError(
            f"Model returned wrong categories. missing={list(missing)}, extra={list(extra)}"
        )

    return result