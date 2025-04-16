import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI, OpenAI

azure_credential = None
openai_client = None
openai_model_arg = None


def get_azure_credential():
    """
    Get the Azure credential for authentication.
    This function uses the DefaultAzureCredential from the azure.identity package.
    It will first check if the credential is already set. If not, creates a new one.
    """
    global azure_credential

    if azure_credential is None:
        azure_credential = DefaultAzureCredential(
            exclude_shared_token_cache_credential=True
        )
        return azure_credential


def configure_openai_client():
    """
    Configure the OpenAI client based on environment variables set for Azure or OpenAI.

    This function checks for the presence of the AZURE_OPENAI_ENDPOINT and
    OPENAI_API_KEY environment variables.

    If AZURE_OPENAI_ENDPOINT is set, it configures the client for Azure OpenAI.
    Otherwise, it configures for standard OpenAI.

    It also sets the API version and deployment name for Azure OpenAI if applicable.
    If neither environment variable is set, it raises a ValueError.
    """
    global openai_client, openai_model_arg

    if openai_client:
        return openai_client, openai_model_arg

    if os.getenv("AZURE_OPENAI_ENDPOINT"):
        # Configure for Azure OpenAI
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        client_args = {}
        if api_key:
            client_args["api_key"] = api_key
        else:
            client_args["azure_ad_token_provider"] = get_bearer_token_provider(
                get_azure_credential(), "https://cognitiveservices.azure.com/.default"
            )

        openai_client = AzureOpenAI(
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            **client_args
        )

        openai_model_arg = os.getenv("AZURE_OPENAI_CHATGPT_DEPLOYMENT_NAME")

    elif os.getenv("OPENAI_API_KEY"):
        # Configure for standard OpenAI
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        openai_model_arg = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

    else:
        raise ValueError(
            "No OpenAI configuration provided. Check your environment variables."
        )

    return openai_client, openai_model_arg
