summarizer_system_message = """
You will receive multiple CSV files belonging to a user. 
Summarize the key themes from all files in 2 meaningful paragraphs as a ui/ux enhancment ai tool.
"""

def summarizer_prompt(user_uploads_csv):
    prompt = f"Here are the user's uploaded files in CSV format:\n\n{user_uploads_csv}\n\nWrite the key ui/ux enhancements that can be done in 2-3 paragraphs."
    return prompt
