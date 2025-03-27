import requests
import jwt
import concurrent.futures
import xml.etree.ElementTree as ET
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Domains.Onboard.models import Business
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


def get_web_performance(url):
    cache_key = f"web_metrics_{url}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    api_key = settings.PAGESPEED_API_KEY
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={api_key}"
    response = requests.get(api_url)
    data = response.json()

    metrics = {
        "First Contentful Paint": data["lighthouseResult"]["audits"]["first-contentful-paint"]["displayValue"],
        "Speed Index": data["lighthouseResult"]["audits"]["speed-index"]["displayValue"],
        "Largest Contentful Paint (LCP)": data["lighthouseResult"]["audits"]["largest-contentful-paint"]["displayValue"],
        "Time to Interactive": data["lighthouseResult"]["audits"]["interactive"]["displayValue"],
        "Total Blocking Time (TBT)": data["lighthouseResult"]["audits"]["total-blocking-time"]["displayValue"],
        "Cumulative Layout Shift (CLS)": data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["displayValue"]
    }

    cache.set(cache_key, metrics, timeout=60 * 60)
    return metrics


def get_page_xml(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Try to parse XML
        root = ET.fromstring(response.content)

        # Convert it into a dictionary-like list of tag names and text
        parsed = []
        for elem in root.iter():
            parsed.append({elem.tag: elem.text.strip() if elem.text else ""})

        return {
            "url": url,
            "parsed_xml": parsed[:30]  # return first 30 tags only
        }

    except Exception as e:
        return {"error": f"Could not retrieve XML from {url}: {str(e)}"}

class WebMetricsAPIView(APIView):
    def get(self, request, format=None):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response({"error": "Business not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_url_metrics = executor.submit(get_web_performance, business.url) if business.url else None
            future_role_model_metrics = executor.submit(get_web_performance, business.role_model) if business.role_model else None

            if future_url_metrics:
                results["url_metrics"] = future_url_metrics.result()
            else:
                results["url_metrics"] = "No business URL provided."

            if future_role_model_metrics:
                results["role_model_metrics"] = future_role_model_metrics.result()
            else:
                results["role_model_metrics"] = "No role model URL provided."

        return Response(results, status=status.HTTP_200_OK)

from bs4 import BeautifulSoup

class BusinessHTMLAPIView(APIView):
    def get(self, request, format=None):
        # 1. Extract JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Get Business
        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response({"error": "Business not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        if not business.url:
            return Response({"error": "Business does not have a URL set."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Fetch and parse HTML
        try:
            response = requests.get(business.url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extract common data
            html_data = {
                "url": business.url,
                "title": soup.title.string.strip() if soup.title else None,
                "meta_description": next((meta.get("content") for meta in soup.find_all("meta") if meta.get("name") == "description"), None),
                "headings": {
                    "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
                    "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
                    "h3": [h.get_text(strip=True) for h in soup.find_all("h3")]
                },
                "links": [a.get("href") for a in soup.find_all("a", href=True)][:20]  # limit to 20 links
            }

            return Response(html_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Could not retrieve HTML from {business.url}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class BusinessCSSAPIView(APIView):
    def get(self, request, format=None):
        # 1. JWT Auth
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Get Business
        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response({"error": "Business not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        if not business.url:
            return Response({"error": "Business does not have a URL set."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Fetch & parse HTML
        try:
            response = requests.get(business.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # 4. Extract external stylesheet links
            stylesheet_links = [
                link.get("href") for link in soup.find_all("link", rel="stylesheet") if link.get("href")
            ]

            # 5. Extract inline <style> blocks
            inline_styles = [
                style.get_text(strip=True) for style in soup.find_all("style")
            ]

            return Response({
                "url": business.url,
                "stylesheet_links": stylesheet_links,
                "inline_styles": inline_styles[:3]  # limit to 3 style blocks for readability
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Could not retrieve CSS from {business.url}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
