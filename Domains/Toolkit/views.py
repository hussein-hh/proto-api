import requests
import jwt
import concurrent.futures
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

    # Extract key performance metrics
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
        # Extract JWT from Authorization Header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = parts[1]

        # Decode JWT and retrieve user_id
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the business associated with the user
        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response({"error": "Business not found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        results = {}
        # Use ThreadPoolExecutor to execute both API requests concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_url_metrics = None
            future_role_model_metrics = None

            if business.url:
                future_url_metrics = executor.submit(get_web_performance, business.url)
            else:
                results["url_metrics"] = "No business URL provided."

            if business.role_model:
                future_role_model_metrics = executor.submit(get_web_performance, business.role_model)
            else:
                results["role_model_metrics"] = "No role model URL provided."

            if future_url_metrics is not None:
                results["url_metrics"] = future_url_metrics.result()
            if future_role_model_metrics is not None:
                results["role_model_metrics"] = future_role_model_metrics.result()

        return Response(results, status=status.HTTP_200_OK)
