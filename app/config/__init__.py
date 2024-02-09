"""
Module to settings
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurations generals for connections and JWT
    """

    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_SCHEMA: str = os.getenv("DB_SCHEMA", "dbo")
    DB_HOST: str = os.getenv("DB_HOST", "")

    JWT_SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    REFRESH_TOKEN_EXPIRES_IN: int = 30
    ACCESS_TOKEN_EXPIRES_IN: int = 30
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
