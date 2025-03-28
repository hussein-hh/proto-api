from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv
import Domains.Results.LLMs.prompts as prompts  
from django.core.cache import cache

_ = load_dotenv(find_dotenv())

groq_client = Groq(
    api_key=os.environ.get('GROQ_API_KEY')
)

temperature = 0.1
top_p = 0.1
max_tokens = 2000

def summarizer(user_id, csv_content):
    """
    Sends all user-uploaded CSV content to the LLM for bulk summarization.
    Uses cached summary per user, regenerates only when cache is invalidated.
    """

    cache_key = f"summarizer_output_user_{user_id}"
    cached_summary = cache.get(cache_key)

    if cached_summary: 
        return cached_summary
    
    # If not cached, run summarization
    system_message = prompts.summarizer_system_message
    prompt = prompts.summarizer_prompt(csv_content) 

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    uba_agent = completion.choices[0].message.content

    cache.set(cache_key, uba_agent)

    return uba_agent 

def webAgent(url_metrics, shark_metrics):

    system_message = prompts.webAgent_system_message
    prompt = prompts.webAgent_prompt(url_metrics, shark_metrics) 

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    web_evaluation = completion.choices[0].message.content
    return web_evaluation  

def feynmanAgent(html, css, title=None, headings=None, links=None):
    system_message = prompts.feynman_system_message
    prompt = prompts.feynman_prompt(html, css, title, headings, links)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return completion.choices[0].message.content

def davinciAgent(ui_summary, ux_summary):
    """
    Intakes ui & ux summary from Feynaman & Jobs agents (respectfully) to generate a list of questions.
    """
    system_message = prompts.davinci_system_message
    prompt = prompts.feynman_prompt(ui_summary, ux_summary)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return completion.choices[0].message.content

def einsteinAgent(question, uba_csv, html, css):
    """
    Answers a UX/UI product question using actual data:
    - question: a single product/design question (from Davinci)
    - uba_csv: CSV of user-behavior analytics
    - html/css: Raw HTML & CSS of the target page
    """
    system_message = prompts.einstein_system_message
    prompt = prompts.einstein_prompt(question, uba_csv, html, css)

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt}
    ]

    completion = groq_client.chat.completions.create(
        model="llama3-8b-8192",
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

    return completion.choices[0].message.content
