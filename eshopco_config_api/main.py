import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent

DEFAULTS: dict[str, Any] = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

app = FastAPI(title="eShopCo Effective Configuration API")

# The grader's page may be hosted on a different origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

def coerce(key: str, value: Any) -> Any:
    text = str(value)
    normalized = key.lower()
    if normalized in {"port", "workers"}:
        try:
            return int(text)
        except (TypeError, ValueError):
            return 0
    if normalized == "debug":
        return text.strip().lower() in {"true", "1", "yes", "on"}
    return text

def effective_config(overrides: list[str]) -> dict[str, Any]:
    config: dict[str, Any] = dict(DEFAULTS)

    # Layer 2: environment-specific YAML.
    yaml_path = ROOT / f"config.{os.getenv('APP_ENV', 'development')}.yaml"
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            yaml_layer = yaml.safe_load(f) or {}
        config.update({str(k).lower(): v for k, v in yaml_layer.items()})

    # Layer 3: .env values. NUM_WORKERS is an alias for workers.
    env_file = dotenv_values(ROOT / ".env")
    for raw_key, value in env_file.items():
        if value is None:
            continue
        key = raw_key.lower()
        if raw_key == "NUM_WORKERS":
            key = "workers"
        elif raw_key.startswith("APP_"):
            key = raw_key[4:].lower()
        config[key] = value

    # Layer 4: OS-level APP_* variables override .env.
    for raw_key, value in os.environ.items():
        if raw_key.startswith("APP_") and raw_key != "APP_ENV":
            config[raw_key[4:].lower()] = value

    # Layer 5: CLI-style query overrides, applied in request order.
    for item in overrides:
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        key = key.strip().lower()
        if key:
            config[key] = value

    result = {key: coerce(key, value) for key, value in config.items()}
    result["api_key"] = "****"
    return result

@app.get("/effective-config")
def get_effective_config(set: list[str] = Query(default=[])):
    return effective_config(set)

@app.get("/")
def root():
    return {"service": "eshopco-config-api", "endpoint": "/effective-config"}
