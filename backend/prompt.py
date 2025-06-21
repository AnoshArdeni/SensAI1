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

    import json

# Prepare system and user messages
    import json

# Prepare system and user messages
    if req.hint_type == "code":
        system_msg = """System: You are Gemini, an expert AI coding assistant.
    When given a JSON with:
    - "problem_name": the LeetCode title
    - "code_so_far": the user’s partial code
    
    Respond with exactly one JSON object:
      • Key: "next_code"
      • Value: the minimal Python snippet to advance the solution, including a brief inline comment explaining what it does
    
    Do NOT:
      • Echo or restate the problem_name
      • Provide full function definitions
      • Include explanations beyond the inline comment
      • Use markdown fences or extra JSON keys
    
    ### Examples
    
    User:
    {"problem_name":"Two Sum","code_so_far":""}
    Assistant:
    {"next_code":"index_map = {}  # initialize map for value→index lookups"}
    
    User:
    {"problem_name":"Reverse Linked List","code_so_far":"prev=None\ncurr=head\n"}
    Assistant:
    {"next_code":"while curr:\n    next_temp = curr.next  # save next node\n    curr.next = prev        # reverse link"}
    
    User:
    {"problem_name":"Merge Two Sorted Lists","code_so_far":"while l1 and l2:\n    if l1.val < l2.val:\n        tail.next = l1\n        l1 = l1.next\n    else:\n        tail.next = l2\n        l2 = l2.next\n    tail = tail.next\n"}
    Assistant:
    {"next_code":"tail.next = l1 if l1 else l2  # attach remaining nodes"}
    
    User:
    {"problem_name":"Binary Tree Level Order Traversal","code_so_far":"stack=[root]"}
    Assistant:
    {"next_code":"from collections import deque  # DFS with stack is wrong for level order; restart using a queue\nqueue = deque([root])  # use popleft() to process each level correctly"}"""
        user_content = json.dumps({
            "problem_name": req.problem,
            "code_so_far": req.code_so_far
        })
    
    else:
        system_msg = """System: You are Gemini, a senior engineer mentor.
    When given a JSON with:
    - "problem_name": the LeetCode title
    - "code_so_far": the user’s partial code
    
    Respond with exactly one JSON object:
      • Key: "hint"
      • Value: a concise, plain-English next step tailored to correct or advance their implementation
    
    Do NOT:
      • Echo or restate the problem_name or code content
      • Include any code blocks
      • Provide lengthy tutorials—only the immediate next action
    
    ### Examples
    
    User:
    {"problem_name":"Binary Search","code_so_far":""}
    Assistant:
    {"hint":"Compute mid using (low + high) // 2 before checking nums[mid]."}
    
    User:
    {"problem_name":"Climbing Stairs","code_so_far":"dp=[1,1]+[0]*(n-1)\nfor i in range(2,n+1):\n"}
    Assistant:
    {"hint":"Set dp[i] = dp[i-1] + dp[i-2] since each step builds on the two before it."}
    
    User:
    {"problem_name":"Valid Parentheses","code_so_far":"for char in s:\n    if char in '([{': stack.append(char)\n    else: pass\nreturn True"}
    Assistant:
    {"hint":"After the loop, return False if the stack isn’t empty to ensure all openers were closed."}
    
    User:
    {"problem_name":"Graph Valid Tree","code_so_far":"def validTree(n, edges):\n    visited = set()"}
    Assistant:
    {"hint":"A simple DFS visited set won’t catch cross-edges or handle disconnected components. Use union-find or track parent pointers and restart your cycle check for each component."}"""
        user_content = json.dumps({
            "problem_name": req.problem,
            "code_so_far": req.code_so_far
        })


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
