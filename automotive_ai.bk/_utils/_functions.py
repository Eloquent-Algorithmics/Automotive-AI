"""
This module contains functions to search Google and Bing.
"""
from typing import List

import requests

from . import BING_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID


def search_google(
    query: str,
    num: int = 10,
    start: int = 1,
    fileType: str = None,
    lr: str = None,
    safe: str = "off",
) -> List:
    """
    Search Google and return results.

    :param query: The search query string.
    :param num: Number of search results to return.
    :param start: The first result to retrieve (starts at 1).
    :param fileType: Filter results to a specific file type.
    :param lr: Restricts search to documents written in a particular language.
    :param safe: Search safety level (e.g., off, medium, high).
    :return: A list of search results.
    """

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num,
        "start": start,
        "safe": safe,
    }

    # Add optional parameters if they are provided
    if fileType:
        params["fileType"] = fileType
    if lr:
        params["lr"] = lr

    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        results = []
        if data.get("items"):
            for item in data["items"]:
                results.append(
                    {
                        "title": item["title"],
                        "description": item["snippet"],
                        "link": item["link"],
                    }
                )

        return results

    except requests.exceptions.RequestException:
        return []


def search_bing(query: str, num: int = 10) -> List:
    """
    Search Bing and return results.

    :param query: The search query string.
    :param num: Number of search results to return.
    :return: A list of search results.
    """

    url = "https://api.bing.microsoft.com/v7.0/search"
    headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
    params = {"q": query, "count": num}

    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        data = res.json()
        results = []
        if data.get("webPages"):
            for item in data["webPages"]["value"]:
                results.append(
                    {
                        "title": item["name"],
                        "description": item["snippet"],
                        "link": item["url"],
                    }
                )

        return results

    except requests.exceptions.RequestException:
        return []


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_google",
            "description": "This function allows you to use the Google CSE API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to perform the search on.",
                    },
                    "num": {
                        "type": "integer",
                        "description": "Number of search results to return.",
                    },
                    "start": {
                        "type": "integer",
                        "description": "The first result to retrieve (starts at 1).",
                    },
                    "fileType": {
                        "type": "string",
                        "description": "Filter results to a specific file type.",
                    },
                    "lr": {
                        "type": "string",
                        "description": "Restricts the search to a particular language.",
                    },
                    "safe": {
                        "type": "string",
                        "description": "Search safety level.",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_bing",
            "description": "This function allows you to use the Bing search API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query to perform the search on.",
                    },
                    "num": {
                        "type": "integer",
                        "description": "Number of search results to return.",
                    },
                },
                "required": ["query"],
            },
        },
    },
]

available_functions = {
    "search_google": search_google,
    "search_bing": search_bing,
}
