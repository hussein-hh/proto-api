import requests
import jwt
import os
import base64
import concurrent.futures
import xml.etree.ElementTree as ET
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Domains.Onboard.models import Business, Page
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.permissions import IsAuthenticated
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.utils.text import slugify

User = get_user_model()

def get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        user = User.objects.get(id=user_id)
        return user, None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"
    except User.DoesNotExist:
        return None, "User not found"

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

        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id, business=business)
            target_url = page.url
        except Page.DoesNotExist:
            return Response({"error": "Page not found for the given page_id and user."}, status=status.HTTP_404_NOT_FOUND)

        if not target_url:
            return Response({"error": "Page URL is empty or missing."}, status=status.HTTP_400_BAD_REQUEST)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_metrics = executor.submit(get_web_performance, target_url)
            metrics_result = future_metrics.result()

        return Response({f"{business.name} metrics": metrics_result}, status=status.HTTP_200_OK)

class RoleModelWebMetricsAPIView(APIView):

    def get(self, request, format=None):
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found for the given page_id"},
                            status=status.HTTP_404_NOT_FOUND)

        if not page.business:
            return Response({"error": "Page is not associated with any business."},
                            status=status.HTTP_400_BAD_REQUEST)

        business = page.business

        if not business.role_model:
            return Response({"error": "Business does not have an associated role model."},
                            status=status.HTTP_404_NOT_FOUND)

        role_model = business.role_model
        page_type = page.page_type

        if page_type == "Landing Page":
            role_model_url = role_model.landing_page
        elif page_type == "Search Results Page":
            role_model_url = role_model.results_page
        elif page_type == "Product Page":
            role_model_url = role_model.product_page
        else:
            return Response({"error": "Unknown page type."},
                            status=status.HTTP_400_BAD_REQUEST)

        if not role_model_url:
            return Response({"error": f"No URL configured for {page_type} in the role model."},
                            status=status.HTTP_400_BAD_REQUEST)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_metrics = executor.submit(get_web_performance, role_model_url)
            metrics_result = future_metrics.result()

        response_key = f"{role_model.name} {page_type} metrics"
        return Response({response_key: metrics_result}, status=status.HTTP_200_OK)

class PageHTMLAPIView(APIView):
    def get(self, request, format=None):
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({'error': 'Missing required query parameter: page_id'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({'error': 'Page not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not page.url:
            return Response({'error': 'Page does not have a URL set.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = requests.get(page.url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            html_text = response.text
            soup = BeautifulSoup(html_text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else None
            meta_description = next(
                (m.get('content') for m in soup.find_all('meta', attrs={'name': 'description'}) if m.get('content')),
                None
            )
            headings = {
                'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
                'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
                'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
            }
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href and not href.startswith('javascript'):
                    links.append(href)
                    if len(links) == 20:
                        break
            html_data = {
                'url': page.url,
                'html': html_text,
                'title': title,
                'meta_description': meta_description,
                'headings': headings,
                'links': links
            }
            return Response(html_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Could not retrieve HTML from {page.url}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class PageCSSAPIView(APIView):
    """
    Retrieves CSS details (external stylesheet links and inline style blocks) from the URL
    stored on a Page record.

    Expected query parameter:
        - page_id: ID of the Page.
    """
    def get(self, request, format=None):
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        if not page.url:
            return Response({"error": "Page does not have a URL set."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.get(page.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            stylesheet_links = [
                link.get("href") for link in soup.find_all("link", rel="stylesheet") if link.get("href")
            ]
            inline_styles = [
                style.get_text(strip=True) for style in soup.find_all("style")
            ]
            return Response({
                "url": page.url,
                "stylesheet_links": stylesheet_links,
                "inline_styles": inline_styles[:3]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Could not retrieve CSS from {page.url}: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

class UserPagesView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_401_UNAUTHORIZED)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        pages = Page.objects.filter(user=user)
        data = [
            {
                "id": page.id,
                "type": page.page_type,
                "url": page.url,
            }
            for page in pages
        ]
        return Response(data)
    
class TakeScreenshotAPIView(APIView):
    def get(self, request):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response(
                {"error": "Missing required parameter: page_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response(
                {"error": "Page not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not page.url:
            return Response(
                {"error": "This page does not have a URL set."},
                status=status.HTTP_400_BAD_REQUEST
            )

        api_url = "https://shot.screenshotapi.net/screenshot"
        params = {
            "token": "R9M790E-J3XMT8Y-MA30EFT-JEFE9PK",
            "url": page.url,
            "file_type": "png",
            "full_page": "true",
            "output": "json"
        }

        try:
            ss_response = requests.get(api_url, params=params, timeout=120)
            ss_response.raise_for_status()
            json_data = ss_response.json()
            screenshot_url = json_data.get("screenshot")
            if not screenshot_url:
                return Response(
                    {"error": "Screenshot URL not found in response."},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            return Response({
                "success": "Screenshot captured successfully.",
                "screenshot_url": screenshot_url
            })

        except requests.exceptions.HTTPError as http_err:
            return Response(
                {
                    "error": f"Failed to take screenshot: {http_err}",
                    "response_text": ss_response.text
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Failed to take screenshot: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
