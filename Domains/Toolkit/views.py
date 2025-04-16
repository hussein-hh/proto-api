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
    """
    Endpoint for role model web metrics.

    Expected query parameter:
        - page_id: ID of the Page.

    Process:
      1. Retrieves the Page by page_id.
      2. Retrieves the associated Business via Page.business.
      3. Gets the role_model from the Business.
      4. Determines the page type from Page.page_type.
      5. From the role_model, selects the URL matching the page type:
           - "Landing Page"   → role_model.landing_page
           - "Search Results Page" → role_model.results_page
           - "Product Page"   → role_model.product_page
      6. Computes web metrics for that URL using get_web_performance.
      7. Returns the metrics keyed by "{role_model.name} {page_type} metrics".
    """
    def get(self, request, format=None):
        # Extract the page_id from query parameters
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found for the given page_id"},
                            status=status.HTTP_404_NOT_FOUND)

        # Ensure the page is linked to a business.
        if not page.business:
            return Response({"error": "Page is not associated with any business."},
                            status=status.HTTP_400_BAD_REQUEST)

        business = page.business

        # Ensure the business has an associated role model.
        if not business.role_model:
            return Response({"error": "Business does not have an associated role model."},
                            status=status.HTTP_404_NOT_FOUND)

        role_model = business.role_model
        page_type = page.page_type

        # Determine the appropriate URL based on the page type.
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

        # Get web performance metrics for the selected URL.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_metrics = executor.submit(get_web_performance, role_model_url)
            metrics_result = future_metrics.result()

        response_key = f"{role_model.name} {page_type} metrics"
        return Response({response_key: metrics_result}, status=status.HTTP_200_OK)

class PageHTMLAPIView(APIView):
    """
    Retrieves HTML details (title, meta description, headings, links) from the URL
    stored on a Page record.
    
    Expected query parameter:
        - page_id: ID of the Page.
    """
    def get(self, request, format=None):
        # 1. Extract JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'},
                            status=status.HTTP_401_UNAUTHORIZED)
        token = parts[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        # 2. Retrieve the Page using the provided page_id
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure the Page belongs to the authenticated user via its Business
        if not page.business or page.business.user != user:
            return Response({"error": "You do not have permission to access this page."},
                            status=status.HTTP_403_FORBIDDEN)
        
        if not page.url:
            return Response({"error": "Page does not have a URL set."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Fetch and parse HTML from the Page's URL
        try:
            response = requests.get(page.url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            html_data = {
                "url": page.url,
                "title": soup.title.string.strip() if soup.title else None,
                "meta_description": next(
                    (meta.get("content") for meta in soup.find_all("meta") if meta.get("name") == "description"),
                    None
                ),
                "headings": {
                    "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
                    "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
                    "h3": [h.get_text(strip=True) for h in soup.find_all("h3")]
                },
                "links": [a.get("href") for a in soup.find_all("a", href=True)][:20]
            }
            return Response(html_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Could not retrieve HTML from {page.url}: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)

class PageCSSAPIView(APIView):
    """
    Retrieves CSS details (external stylesheet links and inline style blocks) from the URL
    stored on a Page record.
    
    Expected query parameter:
        - page_id: ID of the Page.
    """
    def get(self, request, format=None):
        # 1. Extract JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'},
                            status=status.HTTP_401_UNAUTHORIZED)
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'},
                            status=status.HTTP_401_UNAUTHORIZED)
        token = parts[1]
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'},
                                status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        # 2. Retrieve the Page using the provided page_id
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure the Page belongs to the authenticated user via its Business
        if not page.business or page.business.user != user:
            return Response({"error": "You do not have permission to access this page."},
                            status=status.HTTP_403_FORBIDDEN)
        
        if not page.url:
            return Response({"error": "Page does not have a URL set."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Fetch and parse HTML from the Page's URL to extract CSS info
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
                "inline_styles": inline_styles[:3]  # limit to 3 style blocks for readability
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
        # 1. Authenticate user via JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload.get("user_id"))
        except Exception as e:
            return Response({'error': f'Invalid token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # 2. Get the Page object using page_id
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            page = Page.objects.get(id=page_id, user=user)
        except Page.DoesNotExist:
            return Response({"error": "Page not found or not owned by you."}, status=status.HTTP_404_NOT_FOUND)
        
        if not page.url:
            return Response({"error": "This page does not have a URL set."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Call ScreenshotAPI.net with updated parameters for troubleshooting
        try:
            api_url = "https://shot.screenshotapi.net/screenshot"
            params = {
                "token": "V3CB992-VGS4ZVJ-G9N5ZPA-DY1VSBM",
                "url": page.url,
                "output": "base64",       # Try "json" or "base64" depending on docs
                "file_type": "png",
                "full_page": "true"
                # Remove "fresh" and "ttl" for initial testing
            }

            ss_response = requests.get(api_url, params=params)
            ss_response.raise_for_status()  # This will raise an error for non-200 responses

            data = ss_response.json()
            image_base64 = data.get("base64")

            if not image_base64:
                return Response({"error": "Screenshot API did not return base64 data.",
                                 "response": data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Save the image file
            screenshot_dir = os.path.join("uploads", "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)

            existing_files = [f for f in os.listdir(screenshot_dir) if f.startswith(f"{page.id}_")]
            file_count = len(existing_files) + 1

            filename = f"{page.id}_{page.page_type.replace(' ', '')}_{file_count}.png"
            filepath = os.path.join(screenshot_dir, filename)

            with open(filepath, "wb") as f:
                f.write(base64.b64decode(image_base64))

            # Update DB with screenshot path
            page.screenshot = filepath
            page.save()

            return Response({
                "message": "Screenshot saved successfully.",
                "file_path": filepath
            }, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as http_err:
            # Log response text for debugging
            error_text = ss_response.text if ss_response is not None else "No response text"
            return Response({
                "error": f"Failed to take screenshot: {str(http_err)}",
                "response_text": error_text
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"Failed to take screenshot: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
