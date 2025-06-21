from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import os

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in .env file")

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize FastAPI app
app = FastAPI(title="LeetCode AI Hint Backend")

# Define request structure
typings = ("code", "theory")
class HintRequest(BaseModel):
    hint_type: str        # "code" or "theory"
    problem: str
    code_so_far: str = ""

@app.post("/generate-hint")
async def generate_hint(req: HintRequest):
    """
    Generate a coding hint based on hint_type:
    - code: return minimal code snippet
    - theory: return strategy in plain English
    """
    # Validate hint_type
    if req.hint_type not in typings:
        raise HTTPException(status_code=400, detail="hint_type must be 'code' or 'theory'.")

    # Prepare system and user messages
    if req.hint_type == "code":
        system_msg = "You are a coding assistant. Respond only with the minimal code snippet needed to progress."
        user_content = (
            f"Problem:\n{req.problem}\n\n"
            f"Code so far:\n{req.code_so_far}\n\n"
            "Generate only a small code snippet to help progress."
        )
    else:
        system_msg = (
            "You are a senior engineer mentor. Explain the next steps and algorithmic approach "
            "in plain English without code."
        )
        user_content = (
            f"Problem:\n{req.problem}\n\n"
            f"Code so far:\n{req.code_so_far}\n\n"
            "Explain the next steps without writing code."
        )

    # Call Gemini API
    try:
        response = model.generate_content(
            f"{system_msg}\n\n{user_content}",
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 150,
            }
        )
        hint = response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    # Structured JSON response
    if req.hint_type == "code":
        return {
            "type": "code",
            "language": "python",
            "snippet": hint
        }
    else:
        return {
            "type": "theory",
            "message": hint
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
