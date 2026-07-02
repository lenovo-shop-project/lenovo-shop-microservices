from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_server: str
    db_name: str
    db_user: str
    db_password: str

    db_driver: str = "ODBC Driver 17 for SQL Server"
    db_encrypt: bool = True
    db_trust_server_certificate: bool = True

    jwt_secret: str
    jwt_algorithm: str = "HS256"

    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

settings = Settings()