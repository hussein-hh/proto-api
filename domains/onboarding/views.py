from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.contrib.auth import get_user_model
from domains.onboarding.models import Business

User = get_user_model()

class OnboardingAPIView(APIView):
    def post(self, request):
        data = request.data
        required_fields = ["category", "url", "name"]

        for field in required_fields:
            if field not in data or not data[field]:
                return Response({f"{field}": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if data["category"] not in dict(Business.CATEGORY_CHOICES):
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def onboarding(request):
    data = request.data
    required_fields = ["category", "url", "name"]

    for field in required_fields:
        if field not in data or not data[field]:
            return Response({f"{field}": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

    if data["category"] not in dict(Business.CATEGORY_CHOICES):
        return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

    # 👇 Mock user creation or retrieval (for testing only!)
    mock_user, _ = User.objects.get_or_create(username="testuser")

    business = Business.objects.create(
        user=mock_user,
        category=data["category"],
        url=data["url"],
        name=data["name"]
    )

    return Response(
        {
            "id": business.id,
            "name": business.name,
            "category": business.category,
            "url": business.url,
        },
        status=status.HTTP_201_CREATED,
    )
