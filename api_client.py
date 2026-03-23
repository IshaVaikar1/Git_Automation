
# api_client.py
import logging
import requests
from retry_handler import retry_with_time_limit

logger = logging.getLogger("automation")


@retry_with_time_limit()
def call_api(method, url, params=None, body=None, headers=None, timeout=60):
    """
    PURE GENERIC API CLIENT.
    No flow logic.
    No token extraction.
    No placeholder replacement.
    Just executes an HTTP request and returns raw response JSON/text.
    """
    method = method.upper()
    logger.info(f"[API] Calling {method} {url}")

    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            json=body,
            headers=headers,
            timeout=timeout
        )

        if not response.ok:
            logger.error(
                f"[API ERROR] {method} {url} failed with status={response.status_code}, "
                f"response_body={response}"
            )
            response.raise_for_status()

        logger.info(f"[API] Success {method} {url} (status={response.status_code})")

        try:
            return response.json()
        except:
            return response.text

    except requests.exceptions.RequestException as e:
        logger.error(f"[API] Error {method} {url}: {e}")
        raise