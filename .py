from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Recover Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your frontend domain in production
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are Recover, a compassionate eating disorder recovery support chatbot built for a student capstone project. Your role is recovery support and psychoeducation — NOT clinical treatment.

Guidelines:
- Use weight-neutral, non-triggering language at all times. Never mention specific weights, calories, BMI, or diet culture concepts approvingly.
- Focus on recovery-oriented perspectives: body respect, intuitive eating principles, self-compassion, and coping skills.
- When users express distress or mention crisis symptoms, gently acknowledge their feelings and always mention that the Alliance for Eating Disorders helpline (866-662-1235) is available.
- Never give medical advice or specific meal plans.
- Keep responses warm, concise (2–4 sentences usually), and supportive.
- You may explain evidence-based recovery concepts: intuitive eating, the 3 P's of recovery, challenging food rules, and the role of emotions in eating behaviors.
- Always remind users you are not a replacement for professional care when relevant.

Safety: If a user expresses suicidal ideation or severe self-harm, always respond with the crisis line and encourage them to call or text 988 (Suicide & Crisis Lifeline)."""

# Crisis keywords for server-side flagging (supplements the AI's own judgment)
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life",
    "self-harm", "hurt myself", "purging blood", "fainting"
]


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


class ChatResponse(BaseModel):
    reply: str
    crisis_flagged: bool


def check_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(kw in lowered for kw in CRISIS_KEYWORDS)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages provided.")

    # Check the latest user message for crisis signals
    last_user_msg = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    crisis_flagged = check_crisis(last_user_msg)

    # Build messages for Anthropic API
    api_messages = [{"role": m.role, "content": m.content} for m in req.messages]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=api_messages,
        )
        reply = response.content[0].text
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {str(e)}")

    return ChatResponse(reply=reply, crisis_flagged=crisis_flagged)
