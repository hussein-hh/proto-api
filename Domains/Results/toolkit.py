import requests
from bs4 import BeautifulSoup
from lxml import etree

def get_web_performance(url):
    api_key = "AIzaSyBbuppk5bZg9Js9exxJxchuaOQ5XdT5hR8" 
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={api_key}"

    response = requests.get(api_url)
    data = response.json()

    # Extract key performance metrics
    metrics = {
        "First Contentful Paint": data["lighthouseResult"]["audits"]["first-contentful-paint"]["displayValue"],
        "Speed Index": data["lighthouseResult"]["audits"]["speed-index"]["displayValue"],
        "Largest Contentful Paint (LCP)": data["lighthouseResult"]["audits"]["largest-contentful-paint"]["displayValue"],
        "Time to Interactive": data["lighthouseResult"]["audits"]["interactive"]["displayValue"],
        "Total Blocking Time (TBT)": data["lighthouseResult"]["audits"]["total-blocking-time"]["displayValue"],
        "Cumulative Layout Shift (CLS)": data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["displayValue"]
    }

    return metrics



def scrape_website_as_xml(url):
    response = requests.get(url)
    response.raise_for_status() 

    soup = BeautifulSoup(response.text, "html.parser")

    root = etree.HTML(str(soup))

    xml_str = etree.tostring(root, pretty_print=True, encoding="utf-8").decode()

    return xml_str



