from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import io
import traceback

app = FastAPI()

# ✅ CORS (Required for grader)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request Model
class CodeRequest(BaseModel):
    code: str

# ✅ Health Check Route
@app.get("/")
def home():
    return {"status": "running"}

# ✅ OPTIONS handler (CORS preflight fix)
@app.options("/code-interpreter")
def options_handler():
    return Response(status_code=200)

# ✅ Main Endpoint
@app.post("/code-interpreter")
def run_code(request: CodeRequest):
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()

    try:
        # Execute user code
        exec(request.code, {})
        output = redirected_output.getvalue()

        return {
            "error": [],
            "result": output
        }

    except Exception as e:
        # Extract correct error line number
        tb = traceback.extract_tb(e.__traceback__)
        line_number = None

        for frame in tb:
            if frame.filename == "<string>":
                line_number = frame.lineno
                break

        # Full traceback text required by grader
        traceback_text = traceback.format_exc()

        return {
            "error": [line_number] if line_number else [],
            "result": traceback_text
        }

    finally:
        sys.stdout = old_stdout
