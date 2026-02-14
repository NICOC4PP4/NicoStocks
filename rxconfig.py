import os

config = rx.Config(
    app_name="reflex_app",
    api_url=os.getenv("API_URL", "http://localhost:8000"),
    cors_allowed_origins=["*"],
)
