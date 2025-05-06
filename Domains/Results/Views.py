# views.py
import json, base64, asyncio, os, requests
from concurrent.futures import ThreadPoolExecutor
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from Domains.Onboard.models import Page
from Domains.ManageData.models import Upload
import re, csv
from django.utils.text import slugify
from pathlib import Path
from django.http import HttpResponse
from rest_framework.response import Response
from Domains.Results.LLMs.agents import describe_structure, describe_styling, evaluate_ui, evaluate_uba, formulate_ui, evaluate_web_metrics, web_search_agent, uba_formulator


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

        # check if report exists; if not, trigger generation
        if not page.ui_report or not os.path.exists(page.ui_report):
            try:
                gen_res = requests.get(f"http://127.0.0.1:8000/ask-ai/describe-page/?page_id={pid}")
                if gen_res.status_code != 200:
                    return Response({"error": "Failed to generate UI report"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                # refresh page object to get new ui_report path
                page.refresh_from_db()
            except Exception as e:
                return Response({"error": f"Error during UI report generation: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # load the report
        try:
            with open(page.ui_report, "r", encoding="utf-8") as f:
                report_data = json.load(f)
        except Exception as e:
            return Response({"error": f"Could not read UI report: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # load screenshot
        try:
            with open(page.screenshot, "rb") as img_f:
                screenshot_b64 = base64.b64encode(img_f.read()).decode()
        except Exception as e:
            return Response({"error": f"Failed to load screenshot: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        business_type = getattr(page.business, "category", "unknown")
        page_type     = getattr(page,        "page_type", "unknown")

        try:
            evaluation = evaluate_ui(report_data, screenshot_b64, business_type, page_type)
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
    
    
class EvaluateUBAAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error":"page_id missing"}, status=400)

        try:
            up = Upload.objects.get(references_page_id=pid)
        except Upload.DoesNotExist:
            return Response({"error":"Upload not found"}, status=404)

        try:
            result = evaluate_uba(up.path)
        except Exception as e:
            return Response({"error":str(e)}, status=500)

        folder = os.path.join("Records", "UBA-REPORTS", pid)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, "uba_report.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"report": result}, f, ensure_ascii=False, indent=2)

        up.uba_report = file_path
        up.save()

        return Response({"uba_report": result, "saved_path": file_path}, status=200)
    
BULLET_REGEX = re.compile(r'^\d+\.\s*(.+)')
CONFIG_REGEX = re.compile(r'^\$(\{.*\})$')

import csv, json, re, unicodedata
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

BULLET_BLOCK_RE  = re.compile(r"^\s*(\d+)\.\s+(.*)")   # 1. …    2. …
CONFIG_LINE_RE   = re.compile(r"^\$\s*(\{.*\})\s*$")   # $ { … }

def slugify(text: str) -> str:
    """
    Very small fallback-slugifier (lowercase, ascii, dash-separated).
    """
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text) or "chart"


PROBLEM_RE = re.compile(
    r"(?m)^\s*1\s*-\s*Problem[:;]\s*(.+?)(?=\n\s*\d+\s*-\s*(?:Problem|Analysis|Solution)|\Z)"
)

class UBAProblemSolutionsAPIView(APIView):
    """
    GET /api/uba-problem-solutions/?page_id=<page_id>
    """
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error": "page_id missing"}, status=400)

        try:
            up = Upload.objects.get(references_page_id=pid)
        except Upload.DoesNotExist:
            return Response({"error": "Upload not found"}, status=404)

        if not up.uba_report or not os.path.exists(up.uba_report):
            return Response({"error": "No UBA report found"}, status=404)

        with open(up.uba_report, encoding="utf-8") as f:
            report_text = json.load(f).get("report", "")

        problems = PROBLEM_RE.findall(report_text)
        if not problems:
            return Response({"error": "No problem clauses found"}, status=400)

        results = []
        for clause in problems:
            try:
                resources = web_search_agent(clause.strip())
            except Exception as e:
                resources = [{"source": None, "summary": f"agent error: {e}"}]

            results.append({
                "problem": clause.strip(),
                "solutions": resources
            })

        return Response({"results": results}, status=200)


class EvaluateWebMetricsAPIView(APIView):
    """
    Accepts JSON body of the form:
    {
      "Some Page metrics": {
        "First Contentful Paint": "1.2 s",
        "Speed Index": "12.8 s",
        "Largest Contentful Paint (LCP)": "27.1 s",
        "Time to Interactive": "28.2 s",
        "Total Blocking Time (TBT)": "390 ms",
        "Cumulative Layout Shift (CLS)": "0"
      }
    }
    Returns the WebMetricsAdvisor JSON.
    """
    def post(self, request):
        # grab the only metrics object in the body
        try:
            raw_metrics = next(iter(request.data.values()))
            if not isinstance(raw_metrics, dict):
                raise ValueError
        except Exception:
            return Response(
                {"error": "Invalid format: send one top-level key with a metrics dict"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result_text = evaluate_web_metrics(raw_metrics)
            result_json = json.loads(result_text)
        except Exception as e:
            return Response(
                {"error": f"Evaluation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response({"web_metrics_report": result_json}, status=status.HTTP_200_OK)


class FormulateUBAAPIView(APIView):
    def get(self, request):
        pid = request.query_params.get("page_id")
        if not pid:
            return Response({"error": "page_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            up = Upload.objects.get(references_page_id=pid)
        except Upload.DoesNotExist:
            return Response({"error": "Upload not found"}, status=status.HTTP_404_NOT_FOUND)

        if not up.uba_report or not os.path.exists(up.uba_report):
            return Response({"error": "UBA report not found"}, status=status.HTTP_404_NOT_FOUND)

        with open(up.uba_report, "r", encoding="utf-8") as f:
            raw = json.load(f).get("report")

        try:
            formulation = uba_formulator(raw)   # now a dict
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # save JSON
        folder = os.path.join("Records", "UBA-FORMULATIONS", pid)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "uba_formulation.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(formulation, f, ensure_ascii=False, indent=2)

        # persist path (ensure your model has this field)
        up.uba_formulation_report = path
        up.save()

        return Response(
            {"uba_formulation": formulation, "saved_path": path},
            status=status.HTTP_200_OK
        )