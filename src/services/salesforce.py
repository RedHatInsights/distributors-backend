"""Salesforce integration service."""

import base64
from logging import Logger
from typing import Any

import jks
from simple_salesforce import Salesforce

from util.logger import get_logger
from util.settings import constants

log: Logger = get_logger(__name__)


def execute_apex(endpoint: str, method: str, data: dict) -> Any:
    """Execute Salesforce Apex REST API call."""
    sf: Salesforce = _get_salesforce()
    return sf.apexecute(endpoint, method=method, data=data)


def _get_salesforce() -> Salesforce:
    private_key: str = _get_private_key()

    log.info(
        f"Connecting to Salesforce: https://{constants.SALESFORCE_DOMAIN}.salesforce.com"
    )

    return Salesforce(
        domain=constants.SALESFORCE_DOMAIN,
        username=constants.SALESFORCE_USERNAME,
        consumer_key=constants.SALESFORCE_CONSUMER_KEY.get_secret_value(),
        privatekey=private_key,
    )


def _get_private_key() -> str:
    try:
        keystore = jks.KeyStore.load(
            constants.SALESFORCE_KEYSTORE_PATH,
            constants.SALESFORCE_KEYSTORE_PASSWORD.get_secret_value(),
        )
        pk_entry = keystore.private_keys[constants.SALESFORCE_CERT_ALIAS]
        pk_entry.decrypt(constants.SALESFORCE_CERT_PASSWORD.get_secret_value())

        return jks.pkey_as_pem(pk_entry)
    except jks.util.BadKeystoreFormatException:
        with open(constants.SALESFORCE_KEYSTORE_PATH, "rb") as f:
            file_contents = f.read()
            log.error(
                f"Full keystore file contents (base64): {base64.b64encode(file_contents).decode()}"
            )
        raise
