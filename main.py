from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import io
import traceback

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/code-interpreter")
def run_code(request: CodeRequest):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        exec(request.code, {})
        output = redirected_output.getvalue()
        return {
            "error": [],
            "result": output
        }

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        line_number = None

        for frame in tb:
            if frame.filename == "<string>":
                line_number = frame.lineno
                break

        return {
            "error": [line_number] if line_number else [],
            "result": ""
        }

    finally:
        sys.stdout = old_stdout
