import os
import asyncio
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import JSONResponse

# Ensure environment variables are loaded
load_dotenv()

# Import the existing agent
from agent.agent import search_agent

app = FastAPI(title="MCP Agent Web")

# CORS (safe defaults; same-origin front-end typically doesn't need this)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    try:
        await search_agent.close()
    except Exception:
        pass


@app.post("/api/chat")
async def api_chat(body: Dict[str, Any]) -> JSONResponse:
    """Send a message to the agent and return its response.

    Body: { "message": str, "max_steps": int (optional), "clear": bool (optional) }
    """
    message = (body or {}).get("message", "").strip()
    max_steps = (body or {}).get("max_steps", 10)
    should_clear = bool((body or {}).get("clear", False))

    if not message:
        return JSONResponse({"error": "message is required"}, status_code=400)

    if should_clear:
        try:
            search_agent.clear_conversation_history()
        except Exception:
            # Non-fatal; continue
            pass

    try:
        response_text = await search_agent.run(message, max_steps=max_steps)
        return JSONResponse({"response": response_text})
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


# Serve the SPA from ./static (expects an index.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")


def run() -> None:
    import uvicorn
    uvicorn.run(
        "web:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )


if __name__ == "__main__":
    run()


