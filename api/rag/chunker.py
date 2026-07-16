"""Recursive character chunking for the PM/PRD document corpus.

Default strategy
----------------
Recursive character splitting targeting ~1000-character chunks with ~150
characters of overlap, splitting on the most semantic boundary available
first (paragraph -> line -> sentence -> word). Markdown documents are
pre-split on headings so a chunk never straddles two sections, which keeps
each chunk topically coherent and gives us a natural title for citations.

Why this strategy
-----------------
PM/PRD reference docs are prose organized under headings. Fixed ~1000-char
chunks are small enough that a retrieved chunk is almost entirely on-topic
(good precision for an FAQ) but large enough to carry a complete idea
(a definition, a framework, a checklist). The 150-char overlap prevents a
sentence that spans a boundary from being cut in half and lost. Heading-aware
splitting means each chunk inherits the section title it came from, which we
store as metadata and surface as a citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
# Boundaries tried in order, from most to least semantic.
_SEPARATORS = ["\n\n", "\n", ". ", " "]


@dataclass
class Chunk:
    text: str
    heading: str
    chunk_index: int
    metadata: dict = field(default_factory=dict)


def _split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Split a markdown doc into (heading, body) sections on ## / ### headings.

    Content before the first heading is returned under the doc's top (#) title
    or an empty heading.
    """
    lines = text.splitlines()
    sections: list[tuple[str, str]] = []
    current_heading = ""
    current_body: list[str] = []

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            # Flush the previous section.
            if current_body or current_heading:
                sections.append((current_heading, "\n".join(current_body).strip()))
            current_heading = m.group(2).strip()
            current_body = []
        else:
            current_body.append(line)

    if current_body or current_heading:
        sections.append((current_heading, "\n".join(current_body).strip()))

    return [(h, b) for h, b in sections if b]


def _recursive_split(text: str, size: int, overlap: int) -> list[str]:
    """Split text into <= size pieces, preferring semantic separators."""
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    # Pick the first separator that actually appears in the text.
    separator = next((s for s in _SEPARATORS if s in text), "")

    pieces: list[str] = []
    if separator:
        parts = text.split(separator)
    else:
        # No separator at all: hard-slice.
        parts = [text[i : i + size] for i in range(0, len(text), size)]
        separator = ""

    buffer = ""
    for part in parts:
        candidate = part if not buffer else buffer + separator + part
        if len(candidate) <= size:
            buffer = candidate
            continue
        # Candidate overflows: emit buffer, then handle the oversized part.
        if buffer:
            pieces.append(buffer)
        if len(part) > size:
            pieces.extend(_recursive_split(part, size, overlap))
            buffer = ""
        else:
            buffer = part
    if buffer:
        pieces.append(buffer)

    # Apply overlap by prefixing each piece with the tail of the previous one.
    if overlap > 0 and len(pieces) > 1:
        overlapped: list[str] = [pieces[0]]
        for prev, cur in zip(pieces, pieces[1:]):
            tail = prev[-overlap:]
            overlapped.append((tail + " " + cur).strip())
        pieces = overlapped

    return [p.strip() for p in pieces if p.strip()]


def chunk_document(
    text: str,
    *,
    source: str,
    title: str = "",
    size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    """Chunk a single markdown document into overlapping, heading-aware chunks."""
    sections = _split_markdown_sections(text)
    if not sections:
        sections = [("", text)]

    chunks: list[Chunk] = []
    idx = 0
    for heading, body in sections:
        for piece in _recursive_split(body, size, overlap):
            heading_label = heading or title or source
            chunks.append(
                Chunk(
                    text=piece,
                    heading=heading_label,
                    chunk_index=idx,
                    metadata={
                        "source": source,
                        "title": title or source,
                        "heading": heading_label,
                    },
                )
            )
            idx += 1
    return chunks
