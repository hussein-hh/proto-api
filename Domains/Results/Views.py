import csv
import io
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from Domains.ManageData.models import Upload
from Domains.Results.LLMs.agents import summarizer 
from Domains.Results.Serializer import UploadSerializer  

@api_view(["GET"])
def get_user_uploads_summary(request, user_id):
    """
    API Endpoint: Retrieves user uploads, converts them to CSV, and sends them to the summarizer agent.
    Returns the summarized response as JSON.
    """
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        uploads_qs = Upload.objects.filter(uploaded_by=user)
        
        if not uploads_qs.exists():
            return Response({"message": "No uploads found for this user."}, status=404)

        uploads_data = UploadSerializer(uploads_qs, many=True).data

        csv_buffer = io.StringIO()
        fieldnames = ["name", "path", "type", "uploaded_at"]
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
        writer.writeheader()
        for upload in uploads_data:
            writer.writerow(upload)

        csv_content = csv_buffer.getvalue()
        csv_buffer.close()

        summary = summarizer(csv_content)

        return Response({
            "user_id": user_id,
            "summary": summary
        }, status=200)

    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
