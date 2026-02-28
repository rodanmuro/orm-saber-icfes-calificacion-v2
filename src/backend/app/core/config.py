from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OMR ICFES Backend"
    app_version: str = "0.1.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    omr_reader_backend: str = "classic"
    omr_default_metadata_path: str = "data/output/template_basica_omr_v2_wireframe.json"
    omr_marked_threshold: float = 0.45
    omr_unmarked_threshold: float = 0.35
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3-flash-preview"
    gemini_timeout_seconds: float = 60.0
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1"
    openai_timeout_seconds: float = 60.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
