"""
Google Docs service layer.
"""
from __future__ import annotations

from typing import Any

from tools.gdocs.auth import get_gdocs_service, GDocsAuthError

__all__ = [
    "GDocsAuthError",
    "read_document",
    "create_document",
]


def read_document(document_id: str) -> str:
    """
    Read text from a Google Doc.
    """
    service = get_gdocs_service()
    doc = service.documents().get(documentId=document_id).execute()
    
    text = ""
    for element in doc.get('body').get('content'):
        if 'paragraph' in element:
            elements = element.get('paragraph').get('elements')
            for elem in elements:
                if 'textRun' in elem:
                    text += elem.get('textRun').get('content')
                    
    return text


def create_document(title: str) -> dict[str, Any]:
    """
    Creates a new blank Google Doc.
    """
    service = get_gdocs_service()
    body = {
        'title': title
    }
    doc = service.documents().create(body=body).execute()
    return doc
