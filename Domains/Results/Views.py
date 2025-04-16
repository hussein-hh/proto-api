import io
import base64
import requests
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Domains.Results.LLMs.agents import generate_caption  

class ImageCaptionAPIView(APIView):
    def get(self, request):
        # Get the page_id from the query parameters; token is no longer required.
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response({"error": "Missing required parameter: page_id"},
                            status=status.HTTP_400_BAD_REQUEST)

        # URL for the updated screenshot API, which now expects page_id as a query param.
        screenshot_url = "http://localhost:8000/toolkit/take-screenshot/"
        try:
            # Call the screenshot API with page_id as query parameter.
            screenshot_response = requests.get(
                screenshot_url,
                params={"page_id": page_id}
            )
            if screenshot_response.status_code != 200:
                return Response({
                    "error": "Screenshot API failed.",
                    "details": screenshot_response.json()
                }, status=screenshot_response.status_code)
        except Exception as e:
            return Response({"error": f"Request to screenshot endpoint failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Extract the file path from the screenshot endpoint's JSON response.
            data = screenshot_response.json()
            screenshot_file_path = data.get("screenshot")
            if not screenshot_file_path:
                return Response({"error": "Screenshot endpoint did not return a screenshot file path."},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Open the screenshot file from disk and process it.
            image = Image.open(screenshot_file_path).convert('RGB')
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            return Response({"error": f"Error processing image: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            # Generate a caption from the base64 image.
            caption = generate_caption(base64_image)
        except Exception as e:
            return Response({"error": f"Captioning failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"description": caption}, status=status.HTTP_200_OK)