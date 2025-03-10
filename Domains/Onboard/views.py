import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Business
from rest_framework.views import APIView

User = get_user_model()

class OnboardingAPIView(APIView):
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data
        required_fields = ["category", "url", "name"]
        for field in required_fields:
            if field not in data or not data[field]:
                return Response({f"{field}": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        if data["category"] not in dict(Business.CATEGORY_CHOICES):
            return Response({"error": "Invalid category."}, status=status.HTTP_400_BAD_REQUEST)

        business = Business.objects.create(
            user=user,
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
