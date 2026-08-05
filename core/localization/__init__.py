"""AerostarLens localization engine.

Pipeline: stock global.ini -> compose enhancements -> merge -> backup -> write
-> validate -> (rollback on failure). Localization text only — see ARCHITECTURE.md §13.
"""
from .apply import apply_enhancements, restore_localization
from .compose import CATEGORY_IDS

__all__ = ["apply_enhancements", "restore_localization", "CATEGORY_IDS"]
