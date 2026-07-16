# Task 3 — Dealing with the Data

## Default chunking strategy

**Recursive character chunking, ~1000 characters per chunk with 150 characters
of overlap, made heading-aware for markdown.** Each document is first split on
its markdown headings so a chunk never straddles two sections; long sections are
then split recursively on the most semantic boundary available (paragraph → line
→ sentence → word). Implemented in `api/rag/chunker.py`. The 9-document corpus
produces **67 chunks**.

**Why this strategy.** The corpus is prose organized under headings, so:

- **~1000 characters** is small enough that a retrieved chunk is almost entirely
  on-topic (good precision for a Q&A assistant) yet large enough to carry a
  complete idea — a definition, a framework, or a checklist.
- **150-character overlap** prevents an idea that spans a boundary from being cut
  in half and lost at retrieval time.
- **Heading-aware splitting** keeps each chunk topically coherent and lets the
  chunk inherit its section title, which we store as metadata and surface in the
  answer as a human-readable citation (e.g. "PRD Structure and Template — Standard
  Sections").

The Task 5 evaluation confirmed this choice retrieves the correct document with
Hit@k = 1.00 and MRR = 1.00; the remaining headroom is precision, addressed in
Task 6.

## Data source (RAG)

A curated knowledge base of **9 product-management / PRD best-practice documents**
(`data/pm_docs/`): what a PRD is, PRD structure and templates, writing user
stories, acceptance criteria, prioritization frameworks (RICE, MoSCoW, Kano),
success metrics and OKRs, non-functional requirements, product discovery and
problem framing, and common PRD mistakes.

**Role in the solution:** this is the private knowledge base the FAQ assistant's
answers are grounded in. Chunks are embedded with OpenAI `text-embedding-3-small`
(1536-d) and stored in **Qdrant Cloud**; at query time the user's question is
embedded and the top-k most similar chunks are retrieved to ground the answer
(RAG). It is the *default* source for any timeless product-management question.

## External API (Agent)

**Tavily** web search (`api/tools/tavily.py`).

**Role in the solution:** it gives the agent access to current, public
information that is not — and should not be — baked into the static corpus:
recent tool releases, vendor features, pricing, trends. It is the agent's tool
for questions the knowledge base cannot answer.

## How they interact during usage

1. The user's question (plus recent conversation as memory) is embedded and the
   top-k chunks are **retrieved from Qdrant** (RAG over the data source).
2. A **router LLM** inspects the question and the retrieved previews and decides
   whether the corpus is sufficient or the question needs current public
   information.
3. If the corpus suffices (e.g. "how do I write acceptance criteria?"), the agent
   answers from it directly. If not (e.g. "what's new in Jira in 2025?"), the
   agent calls the **Tavily** tool and folds the web results in.
4. Corpus chunks and web results are merged into a single numbered context, and
   the answer cites each source with inline `[n]` markers, labelled as knowledge
   base or web.

So the two sources are complementary: the **data source (RAG) is the default and
authority** for product-management knowledge, and the **external API (Tavily) is
the fallback/augmentation** the agent reaches for only when the question demands
freshness — a decision the agent makes itself at step 2.
