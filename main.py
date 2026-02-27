import os
import sys
import traceback
from io import StringIO
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI()

# VERY IMPORTANT (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROOT ROUTE (IMPORTANT FOR TESTER)
@app.get("/")
def root():
    return {"status": "running"}

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

class ErrorAnalysis(BaseModel):
    error_lines: List[int]

# ---------------- EXECUTION TOOL ----------------

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        exec(code)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}
    except Exception:
        return {"success": False, "output": traceback.format_exc()}
    finally:
        sys.stdout = old_stdout

# ---------------- AI ANALYSIS ----------------

def analyze_error_with_ai(code: str, traceback_str: str):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    prompt = f"""
Analyze this Python code and traceback.
Return ONLY JSON like:
{{"error_lines": [line_numbers]}}

CODE:
{code}

TRACEBACK:
{traceback_str}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "error_lines": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.INTEGER),
                    )
                },
                required=["error_lines"],
            ),
        ),
    )

    return ErrorAnalysis.model_validate_json(response.text).error_lines

# ---------------- ENDPOINT ----------------

@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(request: CodeRequest):

    result = execute_python_code(request.code)

    if result["success"]:
        return {"error": [], "result": result["output"]}

    error_lines = analyze_error_with_ai(
        request.code,
        result["output"]
    )

    return {"error": error_lines, "result": result["output"]}
