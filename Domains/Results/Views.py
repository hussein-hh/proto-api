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
from Domains.Results.LLMs.agents import describe_structure, describe_styling, evaluate_ui, evaluate_uba, generate_chart_configs, formulate_ui

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

class GenerateChartsAPIView(APIView):
    """
    1. Ensures UBA evaluation exists, generating it if missing.
    2. Reads the UBA evaluation text and raw UBA data.
    3. Parses numbered observations.
    4. Calls generate_chart_configs to get multiple $<config> lines.
    5. Saves each config under Records/plots/<business_id>/<page_id>/<descriptive-name>.json.
    6. Returns JSON with saved file paths.
    """
    def get(self, request):
        page_id = request.query_params.get("page_id")
        if not page_id:
            return Response({"error": "page_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            up = Upload.objects.get(references_page__id=page_id)
        except Upload.DoesNotExist:
            return Response({"error": "Upload not found"}, status=status.HTTP_404_NOT_FOUND)

        business_id = up.references_page.business.id

        # 1. Generate UBA report if missing
        if not up.uba_report or not Path(up.uba_report).exists():
            try:
                report_text = evaluate_uba(up.path)
                folder_uba = Path("Records") / "UBA-REPORTS" / str(business_id) / str(page_id)
                folder_uba.mkdir(parents=True, exist_ok=True)
                report_path = folder_uba / "uba_report.json"
                with report_path.open("w", encoding="utf-8") as f:
                    json.dump({"report": report_text}, f, ensure_ascii=False, indent=2)
                up.uba_report = str(report_path)
                up.save()
            except Exception as e:
                return Response({"error": f"Error generating UBA report: {e}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Load evaluation report
        try:
            with open(up.uba_report, encoding="utf-8") as f:
                evaluation_text = json.load(f)["report"]
        except Exception as e:
            return Response({"error": f"Cannot load UBA report: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Parse observations
        observations = [
            m.group(1)
            for m in (BULLET_REGEX.match(line) for line in evaluation_text.splitlines())
            if m
        ]

        # 4. Load raw UBA data
        try:
            if up.path.lower().endswith(".csv"):
                with open(up.path, newline="", encoding="utf-8") as f:
                    rows = list(csv.DictReader(f))
                uba_json_str = json.dumps(rows)
            else:
                uba_json_str = Path(up.path).read_text(encoding="utf-8")
        except Exception as e:
            return Response({"error": f"Cannot load UBA data: {e}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 5. Generate chart configs
        raw_configs = generate_chart_configs(evaluation_text, uba_json_str)
        config_lines = [
            m.group(1)
            for m in (CONFIG_REGEX.match(line.strip()) for line in raw_configs.splitlines())
            if m
        ]
        if not config_lines:
            return Response({"error": "No configs produced", "raw": raw_configs},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 6. Save configs as JSON files
        out_folder = Path("Records") / "plots" / str(business_id) / str(page_id)
        out_folder.mkdir(parents=True, exist_ok=True)

        stored = []
        for obs, cfg in zip(observations, config_lines):
            try:
                json.loads(cfg)
            except ValueError:
                continue

            slug = slugify(" ".join(obs.split()[:5])) or "chart"
            file_path = out_folder / f"{slug}.json"
            file_path.write_text(cfg, encoding="utf-8")
            stored.append(str(file_path))

        if not stored:
            return Response({"error": "No configs saved"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"configs_saved": stored}, status=status.HTTP_200_OK)