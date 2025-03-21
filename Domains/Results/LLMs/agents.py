from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv
import Domains.Results.LLMs.prompts as prompts  

_ = load_dotenv(find_dotenv())

groq_client = Groq(
    api_key=os.environ.get('GROQ_API_KEY')
)

temperature = 0.1
top_p = 0.1
max_tokens = 2000

def summarizer(csv_content):
    """
    Sends all user-uploaded CSV content to the LLM for bulk summarization.
    """
    system_message = prompts.summarizer_system_message
    prompt = prompts.summarizer_prompt(csv_content) 

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

    uba_agent = completion.choices[0].message.content
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