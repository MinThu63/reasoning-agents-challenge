"""
External Tools Integration — MCP / API Tools

Provides external tool functions that agents can invoke for grounded retrieval
beyond local documents. Connects to Microsoft Learn and Azure AI Search.

Tools:
    - search_microsoft_learn: Searches Microsoft Learn for certification content
    - query_knowledge_base: Queries the Foundry IQ knowledge base (Azure AI Search)
"""

import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# Tool 1: Microsoft Learn Search (External MCP-equivalent)
# ============================================================

MICROSOFT_LEARN_SEARCH_URL = "https://learn.microsoft.com/api/search"


def search_microsoft_learn(query: str, top: int = 5) -> str:
    """Search Microsoft Learn documentation for certification study resources.

    This is an external tool integration that provides real-time access to
    Microsoft's official documentation. It serves as an MCP-equivalent tool
    that grounds agent responses in authoritative, up-to-date content.

    Args:
        query: Search query (e.g., "AZ-204 Azure Functions")
        top: Number of results to return

    Returns:
        Formatted search results with titles, descriptions, and URLs.
    """
    try:
        params = {
            "search": query,
            "locale": "en-us",
            "$top": top,
            "facet": "category",
            "category": "Documentation",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(MICROSOFT_LEARN_SEARCH_URL, params=params)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if not results:
                    return f"No Microsoft Learn results found for: {query}"

                formatted = []
                for r in results[:top]:
                    title = r.get("title", "Untitled")
                    description = r.get("description", "")[:200]
                    url = r.get("url", "")
                    formatted.append(
                        f"- {title}\n  {description}\n  [source: Microsoft Learn, url: {url}]"
                    )

                return f"Microsoft Learn results for '{query}':\n\n" + "\n\n".join(formatted)
            else:
                return f"Microsoft Learn search returned status {response.status_code}"

    except httpx.TimeoutException:
        return f"Microsoft Learn search timed out for query: {query}"
    except Exception as e:
        return f"Microsoft Learn search error: {e}"


# ============================================================
# Tool 2: Azure AI Search / Foundry IQ Knowledge Base
# ============================================================

def query_knowledge_base(query: str, top: int = 3) -> str:
    """Query the Foundry IQ knowledge base via Azure AI Search.

    Connects to the Azure AI Search index that contains the organization's
    approved certification documentation.

    Args:
        query: Search query
        top: Number of results

    Returns:
        Retrieved passages with citations.
    """
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    search_key = os.getenv("AZURE_SEARCH_API_KEY", "")
    index_name = os.getenv("AZURE_SEARCH_INDEX", "")

    if not search_endpoint or not search_key or not index_name:
        # Fallback: return note that KB is configured but not connected
        return (
            "[Foundry IQ Knowledge Base: Not connected in current environment. "
            "Using local document grounding as fallback. "
            "In production, this would query Azure AI Search index for permission-aware retrieval.]"
        )

    try:
        url = f"{search_endpoint}/indexes/{index_name}/docs/search"
        headers = {
            "api-key": search_key,
            "Content-Type": "application/json",
        }
        body = {
            "search": query,
            "top": top,
            "queryType": "simple",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                url,
                headers=headers,
                json=body,
                params={"api-version": "2023-11-01"},
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("value", [])

                if not results:
                    return f"No knowledge base results for: {query}"

                formatted = []
                for r in results:
                    content = r.get("snippet", "")[:500]
                    source = r.get("blob_url", "unknown")
                    # Extract filename from blob URL
                    source_name = source.split("/")[-1] if "/" in source else source
                    formatted.append(
                        f"- {content}\n  [source: Foundry IQ Knowledge Base, document: {source_name}]"
                    )

                return f"Knowledge Base results for '{query}':\n\n" + "\n\n".join(formatted)
            else:
                return f"Knowledge base query returned status {response.status_code}: {response.text[:200]}"

    except httpx.TimeoutException:
        return f"Knowledge base query timed out for: {query}"
    except Exception as e:
        return f"Knowledge base query error: {e}"


# ============================================================
# Tool Registry
# ============================================================

AVAILABLE_TOOLS = {
    "search_microsoft_learn": {
        "function": search_microsoft_learn,
        "description": "Search Microsoft Learn documentation for certification study resources",
        "used_by": ["learning_path_curator", "assessment_agent"],
    },
    "query_knowledge_base": {
        "function": query_knowledge_base,
        "description": "Query Foundry IQ knowledge base for approved organizational content",
        "used_by": ["learning_path_curator", "assessment_agent"],
    },
}
