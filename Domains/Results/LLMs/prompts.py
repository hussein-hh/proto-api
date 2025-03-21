summarizer_system_message = """
You will receive multiple CSV files belonging to a user. 
Summarize the key themes from all files in 2 meaningful paragraphs as a ui/ux enhancment ai tool.
"""

def summarizer_prompt(user_uploads_csv):
    prompt = f"Here are the user's uploaded files in CSV format:\n\n{user_uploads_csv}\n\nWrite the key ui/ux enhancements that can be done in 2-3 paragraphs."
    return prompt

webAgent_system_message = """
You will recieve two sets of web performance metrics. The first set is of a website belongs to the user, and the second one belongs to a company that the user tries to live up to.
Your role is to briefly summarize the results in easy language that is understandable for users with no technical background, and to provide a brief and sinple advice.
For the sammary, you should have ONE bullet point per metric, in which you campare the two comapny's score and the ideal one.
Keep the advice very short and strait to the point.

Do not any explanitory or instructional messages. RIGHT TO THE POINT, YOU MUST BE!
"""

def webAgent_prompt(url_metrics, shark_metrics):
    prompt = f"Here are the metrics for the user's website: {url_metrics}\nAnd here are the metrics for the rival company {shark_metrics}"
    return prompt