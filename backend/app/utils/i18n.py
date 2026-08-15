import os
from pathlib import Path

from babel.support import Translations

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent.parent / "translations"

_translations_cache: dict[str, Translations] = {}


def get_translations(language: str) -> Translations:
    """Load and cache translations for a given language."""
    if language in _translations_cache:
        return _translations_cache[language]

    locale_dir = str(TRANSLATIONS_DIR)
    if os.path.exists(locale_dir):
        try:
            trans = Translations.load(locale_dir, [language])
            _translations_cache[language] = trans
            return trans
        except Exception:
            pass

    # Fallback: NullTranslations (returns original string)
    from babel.support import NullTranslations

    null_trans = NullTranslations()
    _translations_cache[language] = null_trans
    return null_trans


def gettext(message: str, language: str = "id") -> str:
    """Translate a message string."""
    trans = get_translations(language)
    return trans.gettext(message)


def ngettext(singular: str, plural: str, n: int, language: str = "id") -> str:
    """Translate a singular/plural message string."""
    trans = get_translations(language)
    return trans.ngettext(singular, plural, n)
