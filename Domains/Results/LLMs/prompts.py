summarizer_system_message = """
You are an AI UX analyst. You will receive multiple CSV files containing user behavior analytics (e.g., clicks, scrolls, bounce rates, etc.). 
Your task is to identify key UX themes and usability issues based on the data. 
Summarize the findings into 2 clear and meaningful paragraphs, focusing on how the interface could be improved to enhance user experience.
Avoid technical jargon. Be concise and actionable.
"""

def summarizer_prompt(user_uploads_csv):
    prompt = f"""
The following CSV data contains user interaction logs across several pages of the user's website. 
Please analyze and summarize key user behavior patterns or usability issues that may suggest UI/UX enhancements.

CSV Data:
{user_uploads_csv}

Your output should be 2–3 paragraphs, actionable, and written clearly for a non-technical reader.
"""
    return prompt


webAgent_system_message = """
You will recieve two sets of web performance metrics. The first set is of a website belongs to the user, and the second one belongs to a company that the user tries to live up to.
Your role is to briefly summarize the results in easy language that is understandable for users with no technical background, and to provide a brief and sinple advice.
For the sammary, you should have ONE bullet point per metric, in which you campare the two comapny's score and the ideal one.
Keep the advice very short and strait to the point.

Do not any explanitory or instructional messages. RIGHT TO THE POINT, YOU MUST BE!
"""


def webAgent_prompt(url_metrics, shark_metrics):
    prompt = f"""
Compare the following two sets of metrics:

User Website Metrics:
{url_metrics}

Competitor Website Metrics:
{shark_metrics}

Write one bullet point per metric comparing performance, followed by a short final advice.
"""
    return prompt
