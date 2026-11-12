from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = 'development'
    data_provider: str = 'demo'
    data_api_key: str = ''
    telegram_bot_token: str = ''
    telegram_chat_id: str = ''
    quote_stale_after_seconds: int = 15
    alert_cooldown_seconds: int = 300
    ui_refresh_seconds: int = 1
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()
