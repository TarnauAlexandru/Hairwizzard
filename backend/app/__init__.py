"""Strand backend.

Layers (dependencies point inwards):
    api (presentation) -> application -> strand_core.domain <- infrastructure

FastAPI, the database and the rest arrive in Phase 2.
"""
