import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    caseopen_base_url: str = "http://127.0.0.1:8081"
    adapter_type: str = "mock"
    log_level: str = "INFO"
    app_host: str = "0.0.0.0"
    app_port: int = 5000
    request_timeout: float = 30.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings(
    caseopen_base_url=os.environ.get("CASEOPEN_BASE_URL", "http://127.0.0.1:8081"),
    adapter_type=os.environ.get("ADAPTER_TYPE", "mock"),
    log_level=os.environ.get("LOG_LEVEL", "INFO"),
    app_host=os.environ.get("APP_HOST", "0.0.0.0"),
    app_port=int(os.environ.get("APP_PORT", "5000")),
    request_timeout=float(os.environ.get("REQUEST_TIMEOUT", "30.0")),
)
