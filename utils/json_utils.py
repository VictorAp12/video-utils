"""
This module contains utility functions for loading and saving user settings.
"""

import json
from typing import Literal, Tuple

TRANSLATIONS_PATH = "settings/translations.json"
USER_SETTINGS = "settings/user_settings.json"


def load_last_used_settings() -> (
    Tuple[Literal["pt_BR", "en_US"], Literal["default", "black"]]
):
    """Loads the last used theme and language from the user_settings.json file."""
    with open(USER_SETTINGS, "r", encoding="utf-8") as f:
        user_settings = json.load(f)
        language = user_settings["last_used_language"]

        if not language:
            language = "pt_BR"

        theme = user_settings["last_used_theme"]

        if not theme:
            theme = "default"

    return language, theme


def save_last_used_settings(
    key: Literal["last_used_theme", "last_used_language"],
    theme: Literal["default", "black"] | None = None,
    language: Literal["pt_BR", "en_US"] | None = None,
) -> None:
    """Saves the last used theme and language to the user_settings.json file."""

    last_language, last_theme = load_last_used_settings()

    with open(USER_SETTINGS, "w", encoding="utf-8") as f:

        if key == "last_used_language" and language is not None:
            json.dump({key: language, "last_used_theme": last_theme}, f, indent=4)

        if key == "last_used_theme" and theme is not None:
            json.dump({"last_used_language": last_language, key: theme}, f, indent=4)


def load_translations():
    """Loads the translations from the translations.json file."""
    with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as translation:
        language_translation = json.load(translation)

    return language_translation
