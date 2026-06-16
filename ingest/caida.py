# SPDX-FileCopyrightText: 2026 EU-UNION-AI-PACT
# SPDX-License-Identifier: LicenseRef-UECF-Headquarter-1.0 AND Apache-2.0
"""CAIDA Resource Catalog client (GraphQL).

The catalog API at ``api.catalog.caida.org/v1/`` is a GraphQL endpoint. We issue
a small introspection-free query for catalog objects. Most CAIDA datasets are
governed by the CAIDA Acceptable Use Policy rather than a standard open license.
"""
from __future__ import annotations

from pathlib import Path

from .http import post_json

API_URL = "https://api.catalog.caida.org/v1/"

# The catalog exposes a Relay-style `search` connection over catalog objects
# (datasets, papers, recipes, presentations, ...).
SEARCH_QUERY = """
query Search($query: String!, $first: Int!) {
  search(query: $query, first: $first) {
    totalCount
    edges {
      node {
        id
        name
      }
    }
  }
}
""".strip()


def search(query: str, *, first: int = 25) -> object:
    return post_json(API_URL, {"query": SEARCH_QUERY, "variables": {"query": query, "first": first}})
