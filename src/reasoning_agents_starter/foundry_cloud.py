from __future__ import annotations

from dataclasses import dataclass

from .config import settings


@dataclass(frozen=True)
class CloudSetupResult:
    endpoint: str
    model_deployment: str
    sdk_ready: bool


def validate_cloud_env() -> CloudSetupResult:
    endpoint = settings.azure_ai_project_endpoint.strip()
    deployment = settings.azure_ai_model_deployment.strip()

    if not endpoint:
        raise ValueError("AZURE_AI_PROJECT_ENDPOINT is required for cloud mode.")
    if not deployment:
        raise ValueError("AZURE_AI_MODEL_DEPLOYMENT is required for cloud mode.")

    return CloudSetupResult(endpoint=endpoint, model_deployment=deployment, sdk_ready=False)


def prepare_foundry_client() -> CloudSetupResult:
    result = validate_cloud_env()

    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
    except ImportError as exc:
        raise RuntimeError(
            "Missing cloud dependencies. Install requirements before using cloud mode."
        ) from exc

    _ = AIProjectClient
    _ = DefaultAzureCredential
    return CloudSetupResult(
        endpoint=result.endpoint,
        model_deployment=result.model_deployment,
        sdk_ready=True,
    )