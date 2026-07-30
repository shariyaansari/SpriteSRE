from pydantic_settings import BaseSettings, SettingsConfigDict
#BaseSettings already knows how to load the .env file using the metadata in the model config so there is no need to use dotenv.load_dotenv() explicitly

class Settings(BaseSettings):
    app_name: str = "SpriteSRE"
    github_api_url: str
    github_token: str
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
    )   #Model config to specify the .env file location