"""Minimal local XML hardening helpers used by repo scripts.

This lightweight package provides the subset of ``defusedxml`` used in this
repository so scripts can avoid direct ``xml.etree.ElementTree`` imports while
still rejecting unsafe DTD/entity payloads.
"""

from . import ElementTree

__all__ = ["ElementTree"]
