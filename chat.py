"""
chat.py - Groq API Client integration with context-enforced system prompt, conditional inline citations, and multi-turn conversation memory.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError

# Load environment variables from .env with override=True so edits to .env take effect immediately
load_dotenv(override=True)

DEFAULT_SYSTEM_PROMPT = (
    "You are a factual Q&A and summarization assistant. Answer the user's question or summarize using the provided context below. "
    "Write clear, smooth, well-structured, and natural text. "
    "CRITICAL RULE FOR PAGE CITATIONS: Do NOT include page numbers, page citations, file references, page indexes, or tags like [Source: ...] anywhere in your answer or summary UNLESS the user explicitly asks for page numbers, page indexes, or citations in their prompt. "
    "If internet web search results are provided in the context, use them to enrich the answer, compare facts, or cite external documentation. "
    "WHEN WEB SEARCH RESULTS ARE PROVIDED: ALWAYS list the internet site citations at the VERY END of your response under a section header titled '### Internet Sources' formatted as clickable markdown links: '- [Title](URL)'."
)

CITATION_SYSTEM_PROMPT = (
    "You are a factual Q&A and summarization assistant. Answer the user's question or summarize using the provided context below. "
    "The user explicitly requested page numbers, references, or citations: cite your document sources inline using the exact format "
    "[Source: filename, page X] (or provide a page index / list at the end if asked). "
    "Do not cite sources that were not provided. "
    "If internet web search results are provided in the context, use them to enrich the answer, compare facts, or cite external documentation. "
    "WHEN WEB SEARCH RESULTS ARE PROVIDED: ALWAYS list the internet site citations at the VERY END of your response under a section header titled '### Internet Sources' formatted as clickable markdown links: '- [Title](URL)'."
)

WEB_SEARCH_TRIGGERS = [
    "internet", "web", "online", "site", "website", "search",
    "latest", "google", "original documentation", "official doc",
    "official documentation", "compare with", "compare my document with",
    "external", "find online", "lookup", "citation of the sites", "citations of the sites",
    "sources you used", "sites you used", "where did you get", "what sites"
]


def should_trigger_web_search(query: str, manual_toggle: bool = False) -> bool:
    """
    Determines if internet web search should be executed based on user manual toggle
    or automatic keyword intent detection in the query.
    """
    if manual_toggle:
        return True
    if not query:
        return False
    q = query.lower()
    return any(trig in q for trig in WEB_SEARCH_TRIGGERS)



def get_groq_client() -> OpenAI:
    """
    Instantiates an OpenAI-compatible client pointing to Groq's API endpoint.
    Reads GROQ_API_KEY from environment variables.
    """
    load_dotenv(override=True)
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key == "your_groq_api_key_here":
        api_key = os.getenv("XAI_API_KEY", "").strip()
        if not api_key or api_key == "your_xai_api_key_here":
            raise ValueError(
                "GROQ_API_KEY is missing or invalid. "
                "Please set your Groq API key in the .env file."
            )
        else:
            return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    return client


def format_context_prompt(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    web_chunks: Optional[List[Dict[str, Any]]] = None,
    user_wants_citations: bool = False
) -> str:
    """
    Formats document chunks and web search results into a clean context prompt for the LLM.
    """
    sections = []

    if retrieved_chunks:
        doc_str = ""
        for idx, chunk in enumerate(retrieved_chunks, 1):
            source_file = chunk.get("source_file") or chunk.get("filename") or "document"
            page_num = chunk.get("page", 1)
            if user_wants_citations:
                doc_str += f"[Excerpt {idx} | Source: {source_file}, page {page_num}]:\n{chunk['text']}\n\n"
            else:
                doc_str += f"[Excerpt {idx}]:\n{chunk['text']}\n\n"
        sections.append(f"Context from uploaded documents:\n---------------------\n{doc_str.strip()}\n---------------------")

    if web_chunks:
        web_str = ""
        for idx, wchunk in enumerate(web_chunks, 1):
            title = wchunk.get("title", "Web Site")
            url = wchunk.get("url", "")
            snippet = wchunk.get("snippet", "")
            web_str += f"[Web Result {idx} | Title: {title} | URL: {url}]:\n{snippet}\n\n"
        sections.append(f"Context from Internet Web Search:\n---------------------\n{web_str.strip()}\n---------------------")

    full_context = "\n\n".join(sections)

    prompt = (
        f"{full_context}\n\n"
        f"Current User Question: {query}\n"
        f"Answer:"
    )
    return prompt


def generate_answer(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    model_name: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    web_chunks: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Sends retrieved document context, web search context, multi-turn history, and question to the Groq API and returns the answer.
    
    Args:
        query: User question string.
        retrieved_chunks: List of document context chunk dicts.
        model_name: Model identifier (defaults to GROK_MODEL/GROQ_MODEL env var).
        conversation_history: List of previous message dicts for multi-turn context (capped to last 8 messages / 4 exchanges).
        web_chunks: Optional list of web search result dicts.
        
    Returns:
        String answer generated by Groq API.
    """
    if not retrieved_chunks and not web_chunks:
        return "I don't know. No relevant context was found in the uploaded documents or web search."

    # Determine model to use dynamically at runtime
    if not model_name:
        model_name = os.getenv("GROK_MODEL", "").strip() or os.getenv("GROQ_MODEL", "").strip() or "llama-3.3-70b-versatile"

    # Select system prompt based on whether user explicitly asked for citations/page numbers
    query_lower = query.lower()
    citation_keywords = ["cite", "citation", "citations", "page number", "page numbers", "pages", "reference", "where is", "index of page", "page index", "with page", "show page"]
    user_wants_citations = any(kw in query_lower for kw in citation_keywords)

    system_prompt = CITATION_SYSTEM_PROMPT if user_wants_citations else DEFAULT_SYSTEM_PROMPT

    try:
        client = get_groq_client()
        user_prompt = format_context_prompt(query, retrieved_chunks, web_chunks=web_chunks, user_wants_citations=user_wants_citations)

        # Build messages payload with system prompt, capped conversation history, and current question
        api_messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            # Include up to the last 8 messages (4 exchanges) for conversation memory context
            history_slice = conversation_history[-8:]
            for msg in history_slice:
                if msg.get("role") in ["user", "assistant"] and msg.get("content"):
                    api_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

        api_messages.append({"role": "user", "content": user_prompt})

        response = client.chat.completions.create(
            model=model_name,
            messages=api_messages,
            temperature=0.1,  # Low temperature for factual precision
        )

        answer = response.choices[0].message.content
        return answer.strip()


    except ValueError as ve:
        return f"⚠️ Configuration Error: {str(ve)}"
    except AuthenticationError:
        return "⚠️ Authentication Error: Invalid Groq API key. Please check your GROQ_API_KEY in the .env file."
    except RateLimitError:
        return "⚠️ Rate Limit Error: Exceeded Groq API rate limits. Please wait a moment before trying again."
    except APIConnectionError:
        return "⚠️ Connection Error: Failed to reach Groq API servers. Please check your internet connection."
    except APIError as ae:
        return f"⚠️ Groq API Error ({ae.status_code if hasattr(ae, 'status_code') else 'Unknown'}): {str(ae.message if hasattr(ae, 'message') else ae)}"
    except Exception as e:
        return f"⚠️ Unexpected Error calling Groq API: {str(e)}"


DEFAULT_MODEL = os.getenv("GROK_MODEL", "").strip() or os.getenv("GROQ_MODEL", "").strip() or "llama-3.3-70b-versatile"


class ChatError(Exception):
    """Custom exception class for chat generation errors."""
    pass


get_answer = generate_answer
