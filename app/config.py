from dotenv import load_dotenv
import os
from pydantic_settings import BaseSettings

# Get the parent directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Load the .env file from the parent directory
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)


class Settings(BaseSettings):
    # Postgres/ MySQL/ SQLite
    database_hostname: str
    database_port: str
    database_name: str
    database_username: str
    database_password: str
    secret_key: str
    algorithm: str
    access_token_expire_seconds: int
    class Config:
        env_file = '.env'
settings = Settings()



