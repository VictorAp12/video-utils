"""
This module contains utility functions for loading and saving user settings.
"""

import json
from typing import Literal, Tuple

TRANSLATIONS_PATH = "settings/translations.json"
USER_SETTINGS = "settings/user_settings.json"


def load_last_used_settings() -> Tuple[
    Literal["pt_BR", "en_US"],
    Literal["default", "black"],
    Literal["VideoConverterApp", "ChangeVideoAttributesApp"],
]:
    """
    Loads the last used theme and language from the user_settings.json file.

    :return: A tuple containing the last used theme, language and app.
    """
    with open(USER_SETTINGS, "r", encoding="utf-8") as f:
        user_settings = json.load(f)
        language = user_settings["last_used_language"]

        theme = user_settings["last_used_theme"]

        app = user_settings["last_used_app"]

    f.close()

    return language, theme, app


def save_last_used_settings(
    key: Literal["last_used_theme", "last_used_language"],
    theme: Literal["default", "black"] | None = None,
    language: Literal["pt_BR", "en_US"] | None = None,
    used_app: Literal["VideoConverterApp", "ChangeVideoAttributesApp"] | None = None,
) -> None:
    """
    Saves the last used theme and language to the user_settings.json file.

    :param key: The key to be updated. Must be either "last_used_theme" or "last_used_language".
    :param theme: The new theme to be saved. Must be either "default" or "black".
    :param language: The new language to be saved. Must be either "pt_BR" or "en_US".

    :return: None.
    """

    with open(USER_SETTINGS, "r", encoding="utf-8") as f:
        user_settings = json.load(f)

    if key == "last_used_language" and language is not None:
        user_settings["last_used_language"] = language

    if key == "last_used_theme" and theme is not None:
        user_settings["last_used_theme"] = theme

    user_settings["last_used_app"] = used_app

    with open(USER_SETTINGS, "w", encoding="utf-8") as f:
        json.dump(user_settings, f, indent=4)


def load_translations() -> dict:
    """
    Loads the translations from the translations.json file.

    :return: A dictionary containing the translations.
    """
    with open(TRANSLATIONS_PATH, "r", encoding="utf-8") as translation:
        language_translation = json.load(translation)

    return language_translation
