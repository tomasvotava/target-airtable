import os

import pytest
from dotenv import load_dotenv

from target_airtable.airtable import AirtableClient


@pytest.fixture(name="integration_test_token")
def integration_test_token_fixture() -> str:
    load_dotenv()
    try:
        token = os.environ["AIRTABLE_INTEGRATION_TEST_TOKEN"]
    except KeyError:
        raise RuntimeError("Integration tests can only run if AIRTABLE_INTEGRATION_TEST_TOKEN is set.") from None
    return token


@pytest.fixture()
def integration_test_client(integration_test_token: str) -> AirtableClient:
    return AirtableClient(
        integration_test_token, "appwtyvkFPMTyR40b", "tbluzNJhcZd3aRix6", primary_keys=["Make", "Model"]
    )
