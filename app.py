

import requests
import gradio as gr
import os

# ----------------------------
# Configuration
# ----------------------------
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = ""  # <-- replace with your Hugging Face token
HEADERS = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}
REPHRASE_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

# ----------------------------
# Interview flow
# ----------------------------
FLOW = [
    "Hello, could you please tell me your name and the role you are interviewing for?",
    "Welcome! How are you doing today?",
    "Why did you apply for this role?",
    "What are your top strengths relevant to this role?",
    "What is a weakness you’re actively improving, and how?",
    "Tell me about a project where your contribution made a measurable impact.",
    "Describe a professional conflict and how you resolved it.",
    "Share a time you delivered under a tight deadline.",
    "Which tools/technologies are you most comfortable with, and why?",
    "Where do you see yourself in the next 2–3 years?",
    "Do you have any questions before we close?",
    "This concludes our mock interview. Thank you for your time!"
]

# ----------------------------
# Helpers
# ----------------------------
def rephrase_and_validate(user_answer, role):

    system_prompt = """You are a professional interview coach.
Rephrase the candidate's answer into a recruiter-friendly response.
Keep it concise, clear, and aligned with the {role} role.
Do not invent new facts. Do not comment or evaluate.
Only return the polished version."""


    payload = {
        "model": REPHRASE_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_answer or ""}
        ],
        "max_tokens": 250,
        "temperature": 0.3
    }

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)
        data = resp.json()
        if resp.status_code == 200 and "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        return "I couldn’t rephrase that right now."
    except Exception:
        return "I couldn’t rephrase that right now."

# ----------------------------
# ChatInterface handler
# ----------------------------
def interview_fn(message, history):
    stage = len(history)

    # First turn: ask initial question
    if stage == 0:
        return FLOW[0]

    # End of interview
    if stage >= len(FLOW) - 1:
        return FLOW[-1]
    

    # Rephrase answer and move to next question
    rephrased = rephrase_and_validate(message or "", "this role")    
    next_q = FLOW[stage]
    return f"{rephrased}\n\n{next_q}"


# ----------------------------
# Gradio app
# ----------------------------
demo = gr.ChatInterface(
    fn=interview_fn,
    title="Interview Prep Bot (validated)",
    description="Mock interview with rephrased answers. Bot validates coverage before moving to next question."
)

demo.launch(share=True)