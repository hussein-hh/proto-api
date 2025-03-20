import csv
import io
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Domains.ManageData.models import Upload
from Domains.Results.LLMs.agents import summarizer
from Domains.Results.Serializer import UploadSerializer  

User = get_user_model()

class UserUploadsSummaryAPIView(APIView):
    """
    API Endpoint: Retrieves all uploaded files for the authenticated user,
    converts them to CSV (if applicable), and summarizes key themes.
    """

    def get(self, request):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)

        token = parts[1]

        # Decode JWT token
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve all files uploaded by the user
        uploads = Upload.objects.filter(uploaded_by=user)
        if not uploads.exists():
            return Response({"error": "No files found for this user."}, status=status.HTTP_404_NOT_FOUND)

        # Convert file data to CSV format
        csv_buffer = io.StringIO()
        fieldnames = ["name", "path", "type", "uploaded_at"]
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()

        for upload in uploads:
            writer.writerow(UploadSerializer(upload).data)
        
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        # Generate summary
        summary = summarizer(csv_content)

        return Response({
            "user_id": user_id,
            "summary": summary
        }, status=status.HTTP_200_OK)
