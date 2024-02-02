import logging
import httpx
from storeapi.config import config

logger = logging.getLogger(__name__)


class APIResponseError(Exception):
    pass


async def send_simple_email(to: str, subject: str, body: str):
    logger.debug(f"Sending email to {to}, subject {subject}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Ibrahim <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as error:
            raise APIResponseError(
                f"API failed with status code {error.response.status_code}"
            ) from error


async def send_user_registartion_email(email: str, confirmation_url: str):
    confirmation_message = f"Hello {email}, Thanks for signing up, Please confirm your email using the url {confirmation_url}"

    return await send_simple_email(email, "Confirm Email", confirmation_message)
