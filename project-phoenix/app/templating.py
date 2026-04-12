from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.utils.translations import t

TEMPLATES_DIR = str(Path(__file__).resolve().parent.parent / "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Register translation function as Jinja2 global
# Usage in templates: {{ t("Shop Now", language) }}
templates.env.globals["t"] = t
