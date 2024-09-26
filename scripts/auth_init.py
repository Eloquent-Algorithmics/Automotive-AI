import asyncio
import logging
import os
import subprocess

from auth_common import load_azd_env
from azure.identity import AzureDeveloperCliCredential
from kiota_abstractions.api_error import APIError
from msgraph import GraphServiceClient
from msgraph.generated.applications.item.add_password.add_password_post_request_body import (
    AddPasswordPostRequestBody,
)
from msgraph.generated.models.application import Application
from msgraph.generated.models.implicit_grant_settings import ImplicitGrantSettings
from msgraph.generated.models.password_credential import PasswordCredential
from msgraph.generated.models.web_application import WebApplication
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.WARNING, format="%(message)s", handlers=[RichHandler(rich_tracebacks=True, log_time_format="")]
)
logger = logging.getLogger("authsetup")
logger.setLevel(logging.INFO)


async def check_for_application(client: GraphServiceClient, app_id: str) -> bool:
    try:
        await client.applications.by_application_id(app_id).get()
    except APIError:
        return False
    return True


async def create_application(client: GraphServiceClient) -> Application:
    request_body = Application(
        display_name="WebApp",
        sign_in_audience="AzureADandPersonalMicrosoftAccount",
        web=WebApplication(
            redirect_uris=["http://localhost:50505/redirect"],
            implicit_grant_settings=ImplicitGrantSettings(enable_id_token_issuance=True),
        ),
    )
    return await client.applications.post(request_body)


async def add_client_secret(client: GraphServiceClient, app_id: str) -> str:
    request_body = AddPasswordPostRequestBody(
        password_credential=PasswordCredential(display_name="WebAppSecret"),
    )
    result = await client.applications.by_application_id(app_id).add_password.post(request_body)
    return result.secret_text


def update_azd_env(name, val):
    subprocess.run(f"azd env set {name} {val}", shell=True)


async def main():
    logger.info("Setting up authentication...")
    tenant_id = os.getenv("AZURE_AUTH_TENANT_ID")
    auth_credential = AzureDeveloperCliCredential(tenant_id=tenant_id)

    scopes = ["https://graph.microsoft.com/.default"]
    client = GraphServiceClient(credentials=auth_credential, scopes=scopes)

    app_id = os.getenv("AZURE_AUTH_APP_ID", "no-id")
    if app_id != "no-id":
        logger.info(f"Checking if application {app_id} exists")
        if await check_for_application(client, app_id):
            logger.info("Application already exists, not creating new one")
            exit(0)

    logger.info("Creating application registration")
    app = await create_application(client)

    logger.info(f"Adding client secret to {app.id}")
    client_secret = await add_client_secret(client, app.id)

    logger.info("Updating azd env with AZURE_AUTH_APP_ID, AZURE_AUTH_CLIENT_ID, AZURE_AUTH_CLIENT_SECRET")
    update_azd_env("AZURE_AUTH_APP_ID", app.id)
    update_azd_env("AZURE_AUTH_CLIENT_ID", app.app_id)
    update_azd_env("AZURE_AUTH_CLIENT_SECRET", client_secret)


if __name__ == "__main__":
    load_azd_env()
    asyncio.run(main())
