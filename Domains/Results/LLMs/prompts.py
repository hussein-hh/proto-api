summarizer_system_message = """
You will receive a CSV file and must summarize its content in 3 meaningful words. Focus on key themes.
"""

def summarizer_prompt(user_upload):
    prompt = f"Here the file: {user_upload}"
    return prompt
