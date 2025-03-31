import jwt
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Business, Page, RoleModel

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

        # Validate required fields
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        username = request.data.get("username")
        if not first_name or not last_name or not username:
            return Response(
                {"error": "first_name, last_name, and username are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the user model
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

        # Validate required fields
        name = request.data.get("name")
        category = request.data.get("category")
        role_model_id = request.data.get("role_model")  # expecting an id
        if not name or not category:
            return Response(
                {"error": "Both name and category are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate category against allowed choices
        valid_categories = [choice[0] for choice in Business.CATEGORY_CHOICES]
        if category not in valid_categories:
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

        # Look up RoleModel if provided
        role_model = None
        if role_model_id:
            try:
                role_model = RoleModel.objects.get(id=role_model_id)
            except RoleModel.DoesNotExist:
                return Response({"error": "Role model not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Because Business has a OneToOneField to user, update if it exists or create new.
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
    It will associate the page with the Business linked to the user.
    """
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_401_UNAUTHORIZED)
        user, error = get_user_from_token(token)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)

        # Validate required fields
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

        # Get the associated Business record for this user
        try:
            business = Business.objects.get(user=user)
        except Business.DoesNotExist:
            return Response(
                {"error": "User does not have an associated Business. Please onboard your business first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the Page instance
        page = Page.objects.create(
            page_type=page_type,
            url=url,
            business=business
        )
        return Response({
            "id": page.id,
            "page_type": page.page_type,
            "url": page.url,
            "business": page.business.id if page.business else None,
        }, status=status.HTTP_201_CREATED)
