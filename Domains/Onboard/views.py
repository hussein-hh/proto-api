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
from rest_framework.parsers import MultiPartParser
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

User = get_user_model()

def get_user_from_token(token):
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
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        user_role = request.data.get("user_role")

        if user_role:
            valid_roles = [choice.value for choice in User.UserRole]
            if user_role not in valid_roles:
                return Response(
                    {"error": f"Invalid user_role. Must be one of {valid_roles}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.user_role = user_role

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        user.save()

        return Response({"message": "User onboarded successfully"}, status=status.HTTP_200_OK)
    

class BusinessOnboardingAPIView(APIView):
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
    def post(self, request):
        token = request.data.get("token")
        page_type = request.data.get("page_type")
        url = request.data.get("url")

        if not token or not page_type or not url:
            return Response({"error": "token, page_type and url required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        valid_page_types = [choice[0] for choice in Page.PAGE_TYPE_CHOICES]
        if page_type not in valid_page_types:
            return Response({"error": "Invalid page type."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response(
                {"error": "User has no business. Please onboard business first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        validator = URLValidator()
        try:
            validator(url)
        except ValidationError:

            return Response({
                "id": None,
                "page_type": page_type,
                "url": None,
                "business": business.id,
                "user_id": user.id,
                "html_path": None,
                "css_path": None,
                "screenshot_path": None
            }, status=status.HTTP_200_OK)

        try:
            resp = requests.head(url, timeout=5, allow_redirects=True)
            if resp.status_code >= 400:
                return Response({
                    "id": None,
                    "page_type": page_type,
                    "url": None,
                    "business": business.id,
                    "user_id": user.id,
                    "html_path": None,
                    "css_path": None,
                    "screenshot_path": None
                }, status=status.HTTP_200_OK)
        except requests.RequestException:
            return Response({
                "id": None,
                "page_type": page_type,
                "url": None,
                "business": business.id,
                "user_id": user.id,
                "html_path": None,
                "css_path": None,
                "screenshot_path": None
            }, status=status.HTTP_200_OK)

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

        html_resp = requests.get(f"http://proto-api-kg9r.onrender.com/toolkit/business-html/?page_id={page.id}")
        if html_resp.ok:
            html_data = html_resp.json()
            html_dir = make_dir('Records', 'HTML', str(business.id), str(page.id))
            html_path = os.path.join(html_dir, 'business_html.json')
            with open(html_path, 'w', encoding='utf-8') as f:
                json.dump(html_data, f, ensure_ascii=False, indent=2)
            page.html = os.path.relpath(html_path, settings.BASE_DIR)

        css_resp = requests.get(f"http://proto-api-kg9r.onrender.com/toolkit/business-css/?page_id={page.id}")
        if css_resp.ok:
            css_data = css_resp.json()
            css_dir = make_dir('Records', 'CSS', str(business.id), str(page.id))
            css_path = os.path.join(css_dir, 'business_css.json')
            with open(css_path, 'w', encoding='utf-8') as f:
                json.dump(css_data, f, ensure_ascii=False, indent=2)
            page.css = os.path.relpath(css_path, settings.BASE_DIR)

        try:
            ss_api_resp = requests.get(
                f"http://proto-api-kg9r.onrender.com/toolkit/take-screenshot/?page_id={page.id}",
                timeout=60
            )
            if ss_api_resp.ok:
                data = ss_api_resp.json()
                shot_url = data.get("screenshot_url")
                if shot_url:
                    down = requests.get(shot_url, timeout=120)
                    if down.ok:
                        ss_dir = make_dir('Records', 'SS', str(business.id))
                        ss_path = os.path.join(ss_dir, f'screenshot_{page.id}.png')
                        with open(ss_path, 'wb') as f:
                            f.write(down.content)
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


class ScreenshotUploadAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        token = request.data.get("token")
        page_id = request.data.get("page_id")
        screenshot = request.FILES.get("screenshot")

        if not token or not page_id or not screenshot:
            return Response({"error":"token, page_id & screenshot required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
        except Exception:
            return Response({"error":"Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            page = Page.objects.get(id=page_id, user=user)
        except Page.DoesNotExist:
            return Response({"error":"Page not found or not yours"}, status=status.HTTP_404_NOT_FOUND)

        save_dir = os.path.join("Records", "SS", str(page.business.id))
        os.makedirs(save_dir, exist_ok=True)
        filename = f'screenshot_{page.id}_{screenshot.name}'
        save_path = os.path.join(save_dir, filename)
        with open(save_path, "wb+") as dest:
            for chunk in screenshot.chunks():
                dest.write(chunk)

        page.screenshot = os.path.relpath(save_path, settings.BASE_DIR)
        page.save()

        return Response({"message":"Screenshot uploaded","screenshot_path":page.screenshot}, status=status.HTTP_200_OK)
   
class PageDeleteAPIView(APIView):
    def delete(self, request, page_id, page_type):

        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return Response({"error": "Authorization header required."}, status=401)
        token = auth.split(" ", 1)[1]        
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            page = Page.objects.get(id=page_id, page_type=page_type, user=user)
        except Page.DoesNotExist:
            return Response(
                {"error": "Page not found, type mismatch, or not yours."},
                status=status.HTTP_404_NOT_FOUND
            )

        page.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
