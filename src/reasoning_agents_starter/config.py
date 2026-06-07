from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    azure_ai_project_endpoint: str = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    azure_ai_model_deployment: str = os.getenv("AZURE_AI_MODEL_DEPLOYMENT", "gpt-4o")
    azure_subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    azure_resource_group: str = os.getenv("AZURE_RESOURCE_GROUP", "")
    azure_ai_project_name: str = os.getenv("AZURE_AI_PROJECT_NAME", "")


settings = Settings()
