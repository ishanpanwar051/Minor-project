"""
Backward-compatible module exports for legacy tests/scripts.
"""

from app import create_app
from models import db, User

# Preserve old import style used by legacy tests:
# from eduguard_final import app, db, User
app = create_app()

