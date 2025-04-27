# views.py
import json, base64, asyncio, os
from concurrent.futures import ThreadPoolExecutor
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from Domains.Onboard.models import Page
from Domains.Results.LLMs.agents import describe_structure, describe_styling, evaluate_ui, formulate_ui

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

class EvaluateUIAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error": "page_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        # fetch page record
        try:
            page = Page.objects.get(id=pid)
        except Page.DoesNotExist:
            return Response({"error": "Page not found"}, status=status.HTTP_404_NOT_FOUND)

        # load previously saved UI report
        ui_report_path = page.ui_report
        if not ui_report_path:
            return Response({"error": "UI report not generated"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with open(ui_report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception as e:
            return Response({"error": f"Could not read UI report: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # --- new: load screenshot and fetch metadata ---
        try:
            with open(page.screenshot, "rb") as img_f:
                screenshot_b64 = base64.b64encode(img_f.read()).decode()
        except Exception as e:
            return Response({"error": f"Failed to load screenshot: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        business_type = getattr(page.business, "category", "unknown")
        page_type     = getattr(page,        "page_type", "unknown")

        # call the pure-LLM agent
        try:
            evaluation = evaluate_ui(
                report_data,
                screenshot_b64,
                business_type,
                page_type
            )
        except Exception as e:
            return Response({"error": f"Evaluation failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"evaluation": evaluation}, status=status.HTTP_200_OK)
    
class FormulateUIAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error":"page_id missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            page = Page.objects.get(id=pid)
        except Page.DoesNotExist:
            return Response({"error":"Page not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            evaluation = json.load(open(page.ui_report, "r", encoding="utf-8"))
        except Exception as e:
            return Response({"error":f"Could not read UI report: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            formatted = formulate_ui(evaluation)
        except Exception as e:
            return Response({"error":f"Formulation failed: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        business_id = str(page.business.id)
        folder     = os.path.join("Records", "UI-FORMATS", business_id, pid)
        os.makedirs(folder, exist_ok=True)
        file_path  = os.path.join(folder, "formatted_report.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted)
        page.formatted_report = file_path
        page.save()

        return Response({"formatted_report": formatted, "saved_path": file_path}, status=status.HTTP_200_OK)