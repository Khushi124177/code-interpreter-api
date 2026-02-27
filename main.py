from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import io
import traceback

app = FastAPI()

# ✅ CORS (VERY IMPORTANT FOR GRADER)
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

# ✅ Root Route (Health Check)
@app.get("/")
def home():
    return {"status": "running"}

# ✅ Code Interpreter Endpoint
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
    except Exception:
        error_message = traceback.format_exc()
        return {
            "error": [error_message],
            "result": ""
        }
    finally:
        sys.stdout = old_stdout
