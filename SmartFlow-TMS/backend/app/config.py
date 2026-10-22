from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://smartflow:traffic2024@localhost:5432/traffic_system"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
