import jwt
import os
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Business, Page, RoleModel
import requests


User = get_user_model()

def get_user_from_token(token):
    """
    Helper function to decode JWT and retrieve the user.
    """
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get('user_id')
        if not user_id:
            return None, "Token missing user_id."
        user = User.objects.get(id=user_id)
        return user, None
    except Exception as e:
        return None, f"Invalid or expired token: {str(e)}"

class UserOnboardingAPIView(APIView):
    """
    Endpoint for onboarding/updating a user.
    Expects:
      - token: JWT token.
      - first_name
      - last_name
      - username
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_401_UNAUTHORIZED)
        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        username = request.data.get("username")
        if not first_name or not last_name or not username:
            return Response(
                {"error": "first_name, last_name, and username are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.save()
        return Response({"message": "User onboarded successfully."}, status=status.HTTP_200_OK)


class BusinessOnboardingAPIView(APIView):
    """
    Endpoint for business onboarding.
    Expects:
      - token: JWT token.
      - name: business name.
      - category: business type (must be one of the defined choices).
      - role_model: (optional) RoleModel id.
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_401_UNAUTHORIZED)
        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        name = request.data.get("name")
        category = request.data.get("category")
        role_model_id = request.data.get("role_model") 
        if not name or not category:
            return Response(
                {"error": "Both name and category are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_categories = [choice[0] for choice in Business.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

        role_model = None
        if role_model_id:
            try:
                role_model = RoleModel.objects.get(id=role_model_id)
            except RoleModel.DoesNotExist:
                return Response({"error": "Role model not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        business, created = Business.objects.update_or_create(
            user=user,
            defaults={"name": name, "category": category, "role_model": role_model}
        )
        return Response({
            "id": business.id,
            "name": business.name,
            "category": business.category,
            "role_model": business.role_model.id if business.role_model else None,
        }, status=status.HTTP_201_CREATED)

class PageOnboardingAPIView(APIView):
    """
    Endpoint for page onboarding.
    Expects:
      - token: JWT token.
      - page_type: one of the allowed page types.
      - url: page URL.
    It will associate the page with the Business linked to the user,
    then fetch HTML metadata, CSS metadata, and a screenshot, saving each.
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_401_UNAUTHORIZED)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        page_type = request.data.get("page_type")
        url = request.data.get("url")
        if not page_type or not url:
            return Response(
                {"error": "Both page_type and url are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        valid_page_types = [choice[0] for choice in Page.PAGE_TYPE_CHOICES]
        if page_type not in valid_page_types:
            return Response({"error": "Invalid page type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response(
                {"error": "User does not have an associated Business. Please onboard your business first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        page = Page.objects.create(
            page_type=page_type,
            url=url,
            business=business,
            user=user
        )

        def make_dir(*parts):
            path = os.path.join(settings.BASE_DIR, *parts)
            os.makedirs(path, exist_ok=True)
            return path

        html_resp = requests.get(f"http://127.0.0.1:8000/toolkit/business-html/?page_id={page.id}")
        if html_resp.ok:
            html_data = html_resp.json()
            html_dir = make_dir('Records', 'HTML', str(business.id), str(page.id))
            html_path = os.path.join(html_dir, 'business_html.json')
            with open(html_path, 'w', encoding='utf-8') as f:
                json.dump(html_data, f, ensure_ascii=False, indent=2)
            page.html = os.path.relpath(html_path, settings.BASE_DIR)

        css_resp = requests.get(f"http://127.0.0.1:8000/toolkit/business-css/?page_id={page.id}")
        if css_resp.ok:
            css_data = css_resp.json()
            css_dir = make_dir('Records', 'CSS', str(business.id), str(page.id))
            css_path = os.path.join(css_dir, 'business_css.json')
            with open(css_path, 'w', encoding='utf-8') as f:
                json.dump(css_data, f, ensure_ascii=False, indent=2)
            page.css = os.path.relpath(css_path, settings.BASE_DIR)

        try:
            ss_api_resp = requests.get(
                f"http://127.0.0.1:8000/toolkit/take-screenshot/?page_id={page.id}",
                timeout=60
            )
            if ss_api_resp.ok:
                data = ss_api_resp.json()
                screenshot_url = data.get("screenshot_url")
                if screenshot_url:
                    download_resp = requests.get(screenshot_url, timeout=120)
                    if download_resp.ok:
                        ss_dir = make_dir('Records', 'SS', str(business.id), str(page.id))
                        ss_path = os.path.join(ss_dir, 'screenshot.png')
                        with open(ss_path, 'wb') as f:
                            f.write(download_resp.content)
                        page.screenshot = os.path.relpath(ss_path, settings.BASE_DIR)
        except (requests.RequestException, ValueError):
            pass

        page.save()

        return Response({
            "id": page.id,
            "page_type": page.page_type,
            "url": page.url,
            "business": business.id,
            "user_id": user.id,
            "html_path": page.html,
            "css_path": page.css,
            "screenshot_path": page.screenshot
        }, status=status.HTTP_201_CREATED)

class EvaluateUIAPIView(APIView):
    """
    GET /ask-ai/evaluate-ui/?page_id=<id>
    Loads the stored UI report JSON for the given page and returns it as 'evaluation'.
    """
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error": "page_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=pid)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)

        ui_report_path = page.ui_report
        if not ui_report_path:
            return Response({"error": "ui_report not available for this page"},
                             status=status.HTTP_404_NOT_FOUND)

        try:
            with open(ui_report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"evaluation": report_data}, status=status.HTTP_200_OK)
