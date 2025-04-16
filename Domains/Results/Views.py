import io
import base64
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from Domains.Results.LLMs.agents import generate_caption  

class ImageCaptionAPIView(APIView):

    def post(self, request):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image = Image.open(image_file).convert('RGB')
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG")

            base64_image = base64.b64encode(buffered.getvalue()).decode("utf-8")

            caption = generate_caption(base64_image)
        
        except Exception as e:
            return Response(
                {"error": f"Image captioning with GPT-4o failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({"description": caption}, status=status.HTTP_200_OK)
