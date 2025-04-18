# views.py
import json, base64, asyncio, os
from concurrent.futures import ThreadPoolExecutor
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from Domains.Onboard.models import Page
from Domains.Results.LLMs.agents import describe_structure, describe_styling

executor = ThreadPoolExecutor()

async def run_async(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)

class PageStructureAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid: return Response({"error":"page_id missing"}, status=status.HTTP_400_BAD_REQUEST)
        try: p=Page.objects.get(id=pid)
        except: return Response({"error":"Page not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            html=json.load(open(p.html,"r",encoding="utf-8"))
            css =json.load(open(p.css, "r",encoding="utf-8"))
            img = base64.b64encode(open(p.screenshot,"rb").read()).decode()
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            rpt=describe_structure(img,html,css)
        except Exception as e:
            return Response({"error":str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"structure_report":rpt}, status=status.HTTP_200_OK)

class PageStylingAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error":"page_id missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            p = Page.objects.get(id=pid)
        except:
            return Response({"error":"Page not found"}, status=status.HTTP_404_NOT_FOUND)
        try:
            html = json.load(open(p.html, "r", encoding="utf-8"))
            css = json.load(open(p.css, "r", encoding="utf-8"))
            img = base64.b64encode(open(p.screenshot, "rb").read()).decode()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            rpt = describe_styling(img, html, css)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"styling_report": rpt}, status=status.HTTP_200_OK)
    

class PageUIReportAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error": "page_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            page = Page.objects.get(id=pid)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            html = json.load(open(page.html, "r", encoding="utf-8"))
            css = json.load(open(page.css, "r", encoding="utf-8"))
            image = base64.b64encode(open(page.screenshot, "rb").read()).decode()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        async def get_reports():
            structure_task = run_async(describe_structure, image, html, css)
            styling_task = run_async(describe_styling, image, html, css)
            structure_report, styling_report = await asyncio.gather(structure_task, styling_task)
            return {
                "structure_report": structure_report,
                "styling_report": styling_report
            }

        try:
            report_data = asyncio.run(get_reports())
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            business_id = str(page.business.id)
            page_id = str(page.id)
            folder_path = os.path.join("Records", "UI-REPORTS", business_id, page_id)
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, "ui_report.json")

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

            page.ui_report = file_path
            page.save()

        except Exception as e:
            return Response({"error": f"Error saving report: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "ui_report": report_data,
            "saved_path": file_path
        }, status=status.HTTP_200_OK)
