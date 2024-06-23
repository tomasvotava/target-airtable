import datetime

from target_airtable.airtable import AirtableClient


def test_smoke_test(integration_test_client: AirtableClient) -> None:
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    record = {
        "Make": "Integration",
        "Model": "Test",
        "Year": 2001,
        "Price": 420.69,
        "Created at": now.isoformat(),
        "Updated at": now.isoformat(),
    }

    integration_test_client.upsert_batch([record])
