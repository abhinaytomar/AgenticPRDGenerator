# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

@AGENTS.md

## Build & Development Commands

- `npm run dev` — Start Next.js development server (port 3000)
- `npm run build` — Production build
- `npm run start` — Start production server
- `npm run lint` — Run ESLint

The Python backend (FastAPI) is in `api/index.py`:
- Install deps: `pip install -r requirements.txt`
- Run locally: `uvicorn api.index:app` (runs on port 8000 by default)

Both services must run simultaneously for full functionality. In production on Vercel, the FastAPI backend is deployed as a serverless function automatically.

There are no tests in this project.

## Architecture

This is **PRD Generator**, a SaaS tool that generates Product Requirements Documents from product ideas, with two separate services:

**Frontend — Next.js 16 (Pages Router) + React 19**
- `pages/_app.tsx` — Root wrapper with Clerk auth provider
- `pages/index.tsx` — Landing/marketing page with feature grid
- `pages/product.tsx` — PRD generation form (requires sign-in via Clerk `<SignedIn>`). Contains a form with product name, problem statement, and additional context textarea. Submits via POST and streams the AI response. Signed-out users see a sign-in prompt.

**Backend — FastAPI (Python) in `api/`**
- `api/index.py` — `POST /api` endpoint that accepts a `ProductIdea` model (product_name, problem_statement, context), streams OpenAI (gpt-5-nano) completions via SSE
- System prompt generates six sections: overview & objectives, target users, user stories, functional requirements, non-functional requirements, and success metrics
- Uses `fastapi-clerk-auth` for JWT bearer token validation

**Data flow:** User fills out PRD form → frontend POSTs form data with JWT bearer token to FastAPI → FastAPI validates JWT, builds prompt from product idea, and streams OpenAI response back via SSE → frontend renders streamed markdown in real-time.

## Key Tech Choices

- **Auth**: Clerk (`@clerk/nextjs`) — handles sign-in and sign-up (no subscription/plan gating)
- **Styling**: Tailwind CSS v4 with `@tailwindcss/postcss` (not v3 — config is in CSS via `@theme` inline in `styles/globals.css`, not `tailwind.config.js`). Also uses `@tailwindcss/typography` plugin.
- **SSE client**: `@microsoft/fetch-event-source` for streaming responses
- **Markdown**: `react-markdown` with `remark-gfm` and `remark-breaks` plugins. AI output is rendered inside a `.markdown-content` wrapper which has custom heading/list/spacing styles in `styles/globals.css`.
- **Path alias**: `@/*` maps to project root
- **Deployment**: Vercel (config in `.vercel/project.json`)

## Environment Variables

Required in `.env.local`:
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL` (used by FastAPI for JWT validation)
- `OPENAI_API_KEY` (used by FastAPI to call OpenAI)

## Next.js Version Warning

This project uses **Next.js 16** which has breaking changes from earlier versions. Always consult `node_modules/next/dist/docs/` before writing Next.js code. Do not rely on prior knowledge of Next.js APIs.
