# main.py — application entry point
#
#   uv run uvicorn main:api --reload
#
# Two lines of real work: the composition root builds everything (3.4),
# the HTTP driving adapter exposes it (5.4).
from app.adapters.api.http_handler import create_api
from app.composition import build_application
from app.config import Settings

api = create_api(build_application(Settings()))
