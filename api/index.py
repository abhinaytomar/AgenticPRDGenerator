import os
import time
from collections import defaultdict
from dotenv import load_dotenv  # type: ignore
from fastapi import Depends, FastAPI, Request  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.responses import JSONResponse, StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer  # type: ignore

# Load .env.local so OPENAI_API_KEY is available to the OpenAI client
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(_project_root, ".env.local"))

from api.models import (
    IntakeRequest,
    IntakeResponse,
    GenerateRequest,
    GenerateResponse,
    TicketsRequest,
    TicketsResponse,
    FAQRequest,
    FAQResponse,
)
from api.agents import run_intake, run_research, run_writer, run_revision, run_critic, run_tickets, run_faq
from api.observability import new_request_id, StepTracker, logger
from api.llm import chat_client, CHAT_MODEL

app = FastAPI()

# CORS: allow the browser to call this API directly (e.g. the Next.js dev
# server on :3000 calling the API on :8000, bypassing the dev proxy). Origins
# are configurable via CORS_ORIGINS (comma-separated); "*" allows any.
_cors_env = os.environ.get("CORS_ORIGINS", "*")
_cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk JWT authentication
clerk_config = ClerkConfig(jwks_url=os.environ.get("CLERK_JWKS_URL", ""))
clerk_auth = ClerkHTTPBearer(config=clerk_config)

# In-memory rate limiter: {client_ip: [timestamp, ...]}
RATE_LIMIT = 10
RATE_WINDOW = 3600  # 1 hour in seconds
request_log: dict[str, list[float]] = defaultdict(list)


class ProductIdea(BaseModel):
    product_name: str
    problem_statement: str
    context: str = ""


system_prompt = """
You are a senior product manager. Given a product idea, generate a comprehensive
Product Requirements Document (PRD). Reply with exactly these sections:

### Overview & Objectives
### Target Users
### User Stories
### Functional Requirements
### Non-Functional Requirements
### Success Metrics
"""


def user_prompt_for(idea: ProductIdea) -> str:
    return f"""Generate a PRD for the following product idea:
Product Name: {idea.product_name}
Problem Statement: {idea.problem_statement}
Additional Context:
{idea.context}"""


def check_rate_limit(user_id: str) -> bool:
    """Return True if the request is allowed, False if rate-limited."""
    now = time.time()
    timestamps = request_log[user_id]
    # Remove entries older than the window
    request_log[user_id] = [t for t in timestamps if now - t < RATE_WINDOW]
    if len(request_log[user_id]) >= RATE_LIMIT:
        return False
    request_log[user_id].append(now)
    return True


def prd_to_markdown(prd: dict) -> str:
    """Convert a structured PRD dict to readable markdown."""
    lines: list[str] = []
    lines.append(f"# {prd.get('title', 'PRD')}")
    lines.append("")
    lines.append(f"## Summary")
    lines.append(prd.get("summary", ""))
    lines.append("")
    lines.append("## Problem Statement")
    lines.append(prd.get("problem_statement", ""))
    lines.append("")

    if prd.get("target_users"):
        lines.append("## Target Users")
        for u in prd["target_users"]:
            lines.append(f"- {u}")
        lines.append("")

    if prd.get("goals"):
        lines.append("## Goals")
        for g in prd["goals"]:
            lines.append(f"- {g}")
        lines.append("")

    if prd.get("non_goals"):
        lines.append("## Non-Goals")
        for ng in prd["non_goals"]:
            lines.append(f"- {ng}")
        lines.append("")

    if prd.get("assumptions"):
        lines.append("## Assumptions")
        for a in prd["assumptions"]:
            lines.append(f"- {a}")
        lines.append("")

    if prd.get("functional_requirements"):
        lines.append("## Functional Requirements")
        for fr in prd["functional_requirements"]:
            lines.append(f"### {fr['id']}: {fr['title']}")
            lines.append(fr.get("description", ""))
            lines.append(f"**Priority:** {fr.get('priority', 'N/A')}")
            lines.append("")
            lines.append("**Acceptance Criteria:**")
            for ac in fr.get("acceptance_criteria", []):
                lines.append(f"- {ac}")
            lines.append("")

    if prd.get("non_functional_requirements"):
        lines.append("## Non-Functional Requirements")
        for nfr in prd["non_functional_requirements"]:
            lines.append(f"### {nfr['id']}: {nfr['category']}")
            lines.append(nfr.get("description", ""))
            lines.append(f"**Metric:** {nfr.get('metric', 'N/A')}")
            lines.append("")

    if prd.get("user_flows"):
        lines.append("## User Flows")
        for uf in prd["user_flows"]:
            lines.append(f"### {uf['name']}")
            for i, step in enumerate(uf.get("steps", []), 1):
                lines.append(f"{i}. {step}")
            if uf.get("error_scenarios"):
                lines.append("")
                lines.append("**Error Scenarios:**")
                for es in uf["error_scenarios"]:
                    lines.append(f"- {es}")
            lines.append("")

    if prd.get("success_metrics"):
        lines.append("## Success Metrics")
        for sm in prd["success_metrics"]:
            lines.append(f"- {sm}")
        lines.append("")

    if prd.get("risks"):
        lines.append("## Risks")
        for r in prd["risks"]:
            lines.append(f"- **{r['description']}** (Severity: {r.get('severity', 'N/A')})")
            lines.append(f"  - Mitigation: {r.get('mitigation', 'N/A')}")
        lines.append("")

    if prd.get("open_questions"):
        lines.append("## Open Questions")
        for oq in prd["open_questions"]:
            lines.append(f"- {oq}")
        lines.append("")

    if prd.get("dependencies"):
        lines.append("## Dependencies")
        for d in prd["dependencies"]:
            lines.append(f"- {d}")
        lines.append("")

    if prd.get("release_considerations"):
        lines.append("## Release Considerations")
        for rc in prd["release_considerations"]:
            lines.append(f"- {rc}")
        lines.append("")

    return "\n".join(lines)


# ── Legacy endpoint (preserved) ───────────────────────────────────────────

@app.post("/api")
def generate_prd(
    idea: ProductIdea,
    request: Request,
):
    client_ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. You can generate up to 5 PRDs per hour. Please try again later."},
        )

    client = chat_client()

    user_prompt = user_prompt_for(idea)

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=prompt,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── New agentic endpoints ─────────────────────────────────────────────────

@app.post("/api/intake")
def intake_endpoint(request_body: IntakeRequest, request: Request, auth=Depends(clerk_auth)):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    request_id = new_request_id()
    tracker = StepTracker(request_id)
    logger.info("request_id=%s endpoint=intake product=%s", request_id, request_body.product_name)

    result = run_intake(request_body, tracker)
    return result.model_dump()


@app.post("/api/generate")
def generate_endpoint(request_body: GenerateRequest, request: Request, auth=Depends(clerk_auth)):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    request_id = new_request_id()
    tracker = StepTracker(request_id)
    logger.info("request_id=%s endpoint=generate product=%s", request_id, request_body.intake.product_name)

    # Step 1: Research
    research = run_research(request_body.intake, request_body.answers, tracker)

    # Step 2: Write PRD
    prd = run_writer(request_body.intake, request_body.answers, research, tracker)

    # Step 3: Critic evaluation
    evaluation = run_critic(prd, tracker)

    # Step 4: If not ready, revise and re-evaluate (fallback to original on failure)
    revision_applied = False
    if evaluation.readiness == "needs_revision":
        try:
            revised_prd = run_revision(prd, evaluation, tracker)
            revised_eval = run_critic(revised_prd, tracker)
            prd = revised_prd
            evaluation = revised_eval
            revision_applied = True
        except Exception as exc:
            logger.warning("request_id=%s revision failed, using original PRD: %s", request_id, exc)

    # Convert to markdown
    prd_markdown = prd_to_markdown(prd.model_dump())

    return GenerateResponse(
        prd=prd,
        evaluation=evaluation,
        revision_applied=revision_applied,
        prd_markdown=prd_markdown,
        meta=tracker.build_meta(),
    ).model_dump()


@app.post("/api/tickets")
def tickets_endpoint(request_body: TicketsRequest, request: Request, auth=Depends(clerk_auth)):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    request_id = new_request_id()
    tracker = StepTracker(request_id)
    logger.info("request_id=%s endpoint=tickets", request_id)

    result = run_tickets(request_body.prd, tracker)
    return result.model_dump()


@app.post("/api/faq")
def faq_endpoint(request_body: FAQRequest, request: Request, auth=Depends(clerk_auth)):
    """Agentic RAG FAQ: retrieve from the PM/PRD corpus + optional web search."""
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please try again later."},
        )

    request_id = new_request_id()
    tracker = StepTracker(request_id)
    logger.info("request_id=%s endpoint=faq q=%s", request_id, request_body.question[:80])

    result = run_faq(request_body.question, request_body.history, tracker)
    return result.model_dump()
