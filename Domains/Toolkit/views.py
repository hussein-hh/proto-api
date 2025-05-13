import os
import re
import jwt
import os
import json
import base64
import requests
import concurrent.futures
import xml.etree.ElementTree as ET

from collections import Counter
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from django.conf import settings
from django.http import HttpResponse
from django.utils.text import slugify
from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pathlib import Path
from Domains.Onboard.models import Business, Page, RoleModelPage

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
    if not api_key:
        raise ValueError("PageSpeed API key is not configured")

    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy=mobile&key={api_key}"
    try:
        response = requests.get(api_url, timeout=300)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"PageSpeed API error: {data['error']['message']}")

        if "lighthouseResult" not in data or "audits" not in data["lighthouseResult"]:
            raise ValueError("Invalid response format from PageSpeed API")

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
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to fetch metrics from PageSpeed API: {str(e)}")
    except (KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid response from PageSpeed API: {str(e)}")

class WebMetricsAPIView(APIView):
    def options(self, request, *args, **kwargs):
        # This method is needed to handle preflight CORS requests
        return Response(
            status=status.HTTP_200_OK,
            headers={
                'Access-Control-Allow-Origin': 'https://proto-ux.netlify.app',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Authorization, Content-Type',
                'Access-Control-Allow-Credentials': 'true',
            }
        )
        
    def get(self, request, format=None):
        # Ensure we're including CORS headers in our response
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

        # Check if metrics already exist
        metrics_dir = os.path.join('Records', 'web_metrics', 'business')
        metrics_path = os.path.join(metrics_dir, f'{page_id}.json')
        
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    stored_metrics = json.load(f)
                    # Store the relative path in the wpm field
                    page.wpm = os.path.relpath(metrics_path)
                    page.save()
                return Response(stored_metrics, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                pass

        try:
            # If no stored metrics or corrupted, fetch new ones
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_metrics = executor.submit(get_web_performance, target_url)
                metrics_result = future_metrics.result()

            # Save metrics to file
            os.makedirs(metrics_dir, exist_ok=True)
            metrics_data = {f"{business.name} metrics": metrics_result}
            with open(metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=2)
            
            # Store the relative path in the wpm field
            page.wpm = os.path.relpath(metrics_path)
            page.save()

            return Response(metrics_data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({"error": f"Failed to get web metrics: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RoleModelWebMetricsAPIView(APIView):
    def options(self, request, *args, **kwargs):
        # This method is needed to handle preflight CORS requests
        return Response(
            status=status.HTTP_200_OK,
            headers={
                'Access-Control-Allow-Origin': 'https://proto-ux.netlify.app',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Authorization, Content-Type',
                'Access-Control-Allow-Credentials': 'true',
            }
        )

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

        if not getattr(page, 'business', None):
            return Response({"error": "Page is not associated with any business."},
                            status=status.HTTP_400_BAD_REQUEST)
        business = page.business

        role_model = getattr(business, 'role_model', None)
        if not role_model:
            return Response({"error": "Business does not have an associated role model."},
                            status=status.HTTP_404_NOT_FOUND)

        page_type = page.page_type

        try:
            rm_page = RoleModelPage.objects.get(role_model=role_model, page_type=page_type)
        except RoleModelPage.DoesNotExist:
            return Response({"error": f"No URL configured for '{page_type}' in role model pages."},
                            status=status.HTTP_404_NOT_FOUND)

        role_model_url = getattr(rm_page, 'url', None)
        if not role_model_url:
            return Response({"error": f"No URL set on RoleModelPage for '{page_type}'."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if metrics already exist
        metrics_dir = os.path.join('Records', 'web_metrics', 'role_model')
        metrics_path = os.path.join(metrics_dir, f'{role_model.id}.json')
        
        if os.path.exists(metrics_path):
            try:
                with open(metrics_path, 'r', encoding='utf-8') as f:
                    stored_metrics = json.load(f)
                    # Store the relative path in the wpm field
                    rm_page.wpm = os.path.relpath(metrics_path)
                    rm_page.save()
                return Response(stored_metrics, status=status.HTTP_200_OK)
            except json.JSONDecodeError:
                pass

        # If no stored metrics or corrupted, fetch new ones
        metrics_result = get_web_performance(role_model_url)

        # Save metrics to file
        os.makedirs(metrics_dir, exist_ok=True)
        metrics_data = {f"{role_model.name} {page_type} metrics": metrics_result}
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, ensure_ascii=False, indent=2)
        
        # Store the relative path in the wpm field
        rm_page.wpm = os.path.relpath(metrics_path)
        rm_page.save()

        response_key = f"{role_model.name} {page_type} metrics"
        return Response({response_key: metrics_result}, status=status.HTTP_200_OK)


class PageHTMLAPIView(APIView):
    def _build_dom_outline(self, soup, text_limit=50):
        outline, sig_counter = [], Counter()

        for el in soup.find_all():
            ident   = el.get("id")
            classes = el.get("class", [])
            text    = el.get_text(strip=True)

            if not (ident or classes or text):
                continue

            sig_key = f"{el.name}|{' '.join(classes)}|{ident or ''}"
            sig_counter[sig_key] += 1

            outline.append({
                "tag"         : el.name,
                "id"          : ident,
                "classes"     : classes,
                "text_sample" : text[:text_limit] or None,
                "inline_style": el.get("style")
            })

        repeated = {}
        for k, v in sig_counter.items():
            tag, classes, _ = k.split("|", 2)
            compact = f"{tag}|{classes}".strip("|")
            if v > 1:
                repeated[compact] = v
        return outline, repeated

    def get(self, request, format=None):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response(
                {"error": "Missing required query parameter: page_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."},
                            status=status.HTTP_404_NOT_FOUND)

        if not page.url:
            return Response({"error": "Page does not have a URL set."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            resp = requests.get(
                page.url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding
            soup = BeautifulSoup(resp.text, "html.parser")

            for t in soup(["script", "style", "noscript"]):
                t.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else None
            meta_desc = next(
                (m.get("content") for m in soup.find_all(
                    "meta", attrs={"name": re.compile("^description$", re.I)})
                 if m.get("content")),
                None,
            )

            headings = {
                "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
                "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
                "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
            }
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href and not href.lower().startswith("javascript"):
                    links.append(urljoin(page.url, href))
                    if len(links) == 20:
                        break

            tag_counter      = Counter(tag.name for tag in soup.find_all())
            structural_tags  = [tag.name for tag in soup.find_all(
                                   ["section", "article", "nav", "aside", "main"])]
            class_names      = [tag.get("class")
                                for tag in soup.find_all() if tag.get("class")]
            id_names         = [tag.get("id")
                                for tag in soup.find_all() if tag.get("id")]
            text_length      = len(soup.get_text(strip=True))
            num_tags         = len(soup.find_all())

            dom_outline, repeated = self._build_dom_outline(soup)

            html_extract = {
                "url": page.url,
                "title": title,
                "meta_description": meta_desc,
                "headings": headings,
                "links": links,
                "tag_counts": dict(tag_counter),
                "structural_tags": structural_tags,
                "class_names": class_names,
                "id_names": id_names,
                "text_length": text_length,
                "num_tags": num_tags,
                "dom_outline": dom_outline,
                "repeated_signatures": repeated,
            }

            return Response(html_extract, status=status.HTTP_200_OK)

        except Exception as exc:
            return Response(
                {"error": f"Could not retrieve HTML from {page.url}: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PageCSSAPIView(APIView):
    """
    Retrieves external stylesheets (with content, rule count, minified status) 
    and inline style blocks from the given Page.
    """
    def get(self, request, format=None):
        page_id = request.query_params.get('page_id')
        if not page_id:
            return Response({"error": "Missing required query parameter: page_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        if not page.url:
            return Response({"error": "Page does not have a URL set."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = requests.get(page.url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            stylesheet_links = []
            for link_tag in soup.find_all("link", rel="stylesheet"):
                href = link_tag.get("href")
                if href:
                    css_url = href if href.startswith("http") else requests.compat.urljoin(page.url, href)
                    try:
                        css_response = requests.get(css_url, timeout=5)
                        css_response.raise_for_status()
                        css_text = css_response.text[:100000]  

                        rule_count = css_text.count('}')
                        
                        is_minified = (
                            css_text.count('\n') < 5 or
                            max((len(line) for line in css_text.splitlines()), default=0) > 500
                        )

                        stylesheet_links.append({
                            "href": css_url,
                            "content": css_text,
                            "css_rule_count": rule_count,
                            "is_minified": is_minified
                        })
                    except Exception as e:
                        stylesheet_links.append({
                            "href": css_url,
                            "error": str(e)
                        })

            inline_styles = []
            for style_tag in soup.find_all("style"):
                css = style_tag.get_text(strip=True)
                rule_count = css.count('}')
                is_minified = (
                    css.count('\n') < 5 or
                    max((len(line) for line in css.splitlines()), default=0) > 500
                )
                inline_styles.append({
                    "content": css,
                    "css_rule_count": rule_count,
                    "is_minified": is_minified
                })

            return Response({
                "url": page.url,
                "external_stylesheets": stylesheet_links,
                "inline_styles": inline_styles[:3]  
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Could not retrieve CSS from {page.url}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



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
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response({"error": "Page not found."}, status=status.HTTP_404_NOT_FOUND)

        if not page.url:
            return Response({"error": "This page does not have a URL set."},
                            status=status.HTTP_400_BAD_REQUEST)

        api_url = "https://shot.screenshotapi.net/screenshot"
        params = {
            "token": "RPNE9GA-2BP4KTF-JKS2K7Z-RZBR7YK",
            "url": page.url,
            "file_type": "png",
            "full_page": "true",
            "lazy_load": "true",   
            "wait_for_event": "networkidle",
            "delay": "2000",          
            "no_cookie_banners": "true", 
            "output": "json",
        }

        try:
            resp = requests.get(api_url, params=params, timeout=150)
            resp.raise_for_status()
            shot_url = resp.json().get("screenshot")
            if not shot_url:
                return Response({"error": "Screenshot URL not returned."},
                                status=status.HTTP_502_BAD_GATEWAY)

            head = requests.head(shot_url, timeout=10)
            content_type = head.headers.get("Content-Type", "")
            content_length = int(head.headers.get("Content-Length", 0))

            if head.status_code != 200 or not content_type.startswith("image/"):
                return Response(
                    {"error": "Screenshot failed—got non-image response."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            if content_length < 100_000:   
                return Response(
                    {"error": "Screenshot empty or placeholder image (too small)."},
                    status=status.HTTP_502_BAD_GATEWAY,
                )
            # -------------------------

            return Response(
                {"success": "Screenshot captured successfully.", "screenshot_url": shot_url}
            )

        except requests.exceptions.HTTPError as e:
            return Response(
                {"error": f"Screenshot API error: {e}", "response_text": resp.text},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Failed to take screenshot: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuickChartAPIView(APIView):
    def get(self, request):
        config = request.query_params.get('config')
        if not config:
            return Response({'error': 'Missing required query parameter: config'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            json.loads(config)
        except ValueError:
            return Response({'error': 'Invalid JSON in config'}, status=status.HTTP_400_BAD_REQUEST)
        resp = requests.get('https://quickchart.io/chart', params={'c': config})
        if resp.status_code == 200:
            return HttpResponse(resp.content, content_type='image/png')
        return Response({'error': 'Chart generation failed'}, status=status.HTTP_502_BAD_GATEWAY)
    

class UserNameAPIView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]
        user, error = get_user_from_token(token)
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_200_OK)
    
class ListChartConfigsAPIView(APIView):
    """
    GET /toolkit/list-plots/<page_id>/
    or
    GET /toolkit/list-chart-configs/?page_id=<page_id>
    """
    def get(self, request, page_id=None):
        # if it wasn't provided in the URL, grab from querystring
        if page_id is None:
            page_id = request.query_params.get("page_id")
        if not page_id:
            return Response(
                {"error": "Missing required parameter: page_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # look up the Page
        try:
            page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return Response(
                {"error": "Page not found for given page_id"},
                status=status.HTTP_404_NOT_FOUND
            )

        biz_id = page.business.id
        folder = Path("Records") / "plots" / str(biz_id) / str(page_id)

        if not folder.exists():
            return Response({"configs": []}, status=status.HTTP_200_OK)

        configs = []
        for fn in folder.glob("*.json"):
            try:
                cfg = json.loads(fn.read_text(encoding="utf-8"))
                configs.append({
                    "slug": fn.stem,
                    "config": cfg
                })
            except Exception:
                continue

        return Response({"configs": configs}, status=status.HTTP_200_OK)
    

