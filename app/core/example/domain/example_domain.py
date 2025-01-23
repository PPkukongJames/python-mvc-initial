"""Example Domain"""

from pydantic import BaseModel


class ExampleDomain(BaseModel):
    """Parameters"""
    word: str
