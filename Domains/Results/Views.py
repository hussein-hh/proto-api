import csv
import io
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from Domains.ManageData.models import Upload
from Domains.Results.LLMs.agents import summarizer, webAgent
from Domains.Results.Serializer import UploadSerializer  

User = get_user_model()

class UserUploadsSummaryAPIView(APIView):
    """
    API Endpoint: Retrieves a specific file uploaded by the authenticated user, 
    converts it to CSV (if applicable), sends it to the summarizer agent, 
    and returns the summarized response as JSON.
    """

    def get(self, request, file_id):
        # Extract token from the "Authorization" header (expects "Bearer <token>").
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return Response({'error': 'Authorization header is required.'}, status=status.HTTP_401_UNAUTHORIZED)

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return Response({'error': 'Authorization header must be in the format: Bearer <token>'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = parts[1]

        # Decode JWT and retrieve user_id.
        try:
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get('user_id')
            if not user_id:
                return Response({'error': 'Token is missing user ID.'}, status=status.HTTP_401_UNAUTHORIZED)
            user = User.objects.get(id=user_id)
        except Exception as e:
            return Response({'error': f'Invalid or expired token: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve file by ID and ensure it belongs to the authenticated user.
        try:
            upload = Upload.objects.get(id=file_id, uploaded_by=user)
        except Upload.DoesNotExist:
            return Response({"error": "File not found or does not belong to the user."}, status=status.HTTP_404_NOT_FOUND)

        upload_data = UploadSerializer(upload).data

        csv_buffer = io.StringIO()
        fieldnames = ["name", "path", "type", "uploaded_at"]
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(upload_data)
        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        summary = summarizer(csv_content)

        return Response({
            "user_id": user_id,
            "file_id": file_id,
            "file_name": upload.name,
            "summary": summary
        }, status=status.HTTP_200_OK)

class WebAgentAPIView(APIView):
    """
    API Endpoint: Accepts two JSON objects (url_metrics and shark_metrics),
    passes them to the webAgent function, and returns the evaluation result.
    """

    def post(self, request):
        # Extract metrics from the request payload.
        url_metrics = request.data.get("url_metrics")
        shark_metrics = request.data.get("shark_metrics")

        if not url_metrics or not shark_metrics:
            return Response(
                {"error": "Both 'url_metrics' and 'shark_metrics' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Call the webAgent function with the provided metrics.
            evaluation = webAgent(url_metrics, shark_metrics)
        except Exception as e:
            return Response(
                {"error": f"An error occurred while processing the request: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Return the evaluation output as JSON.
        return Response({"web_evaluation": evaluation}, status=status.HTTP_200_OK)