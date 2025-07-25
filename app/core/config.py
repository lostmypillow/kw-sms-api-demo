import os
import tomllib
from pathlib import Path

from app.core.lifespan import lifespan


def get_fastapi_config() -> dict:
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        backend_data = tomllib.load(f)

    kwargs = {
        "lifespan": lifespan,
        "title": backend_data.get("project", {}).get("name", "Kw FastAPI Project"),
        "description": backend_data.get("project", {}).get("description", "description here"),
        "version": backend_data.get("project", {}).get("version", "0.0.0"),
    }


    return kwargs