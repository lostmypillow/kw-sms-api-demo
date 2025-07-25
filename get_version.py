import json
try:
    import tomllib 
except ModuleNotFoundError:
    import tomli as tomllib 


from pathlib import Path

backend_pyproject_path = Path("pyproject.toml")


with backend_pyproject_path.open("rb") as f:
    backend_data = tomllib.load(f)
backend_version_str = backend_data.get("project", {}).get("version", "0.0.0")
print(backend_version_str)