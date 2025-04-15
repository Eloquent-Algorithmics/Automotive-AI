from openai import AsyncAzureOpenAI

# Initialize the OpenAI API client
client = AsyncAzureOpenAI(
    api_base="https://your-api-endpoint.azure.com/",
    api_key="your_api_key",
    deployment_name="your_deployment_name"
)
