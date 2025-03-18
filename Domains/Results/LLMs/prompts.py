summarizer_system_message = """
You will recieve a csv file and your mission is to summarize it in three words.
"""

def summarizer_prompt(user_upload):
    prompt = f"Here the file: {user_upload}"
    return prompt
