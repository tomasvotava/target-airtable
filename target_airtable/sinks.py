"""Airtable target sink class, which handles writing streams."""

import datetime
import logging
from decimal import Decimal
from typing import Any, Optional

from singer_sdk import Target
from singer_sdk.sinks import BatchSink

from target_airtable.airtable import AirtableClient

logger = logging.getLogger(__name__)


class AirtableSink(BatchSink):
    """Airtable target sink class."""

    def __init__(
        self, target: Target, stream_name: str, schema: dict[str, Any], key_properties: Optional[list[str]]
    ) -> None:
        logger.warning(schema)
        super().__init__(target, stream_name, schema, key_properties)
        self.current_batch: list[dict[str, Any]] = []
        table_mapping = self.config["table_mapping"]
        if stream_name not in table_mapping:
            raise ValueError(
                f"Stream name {stream_name!r} is not found in table mapping. Please update the configuration."
            )
        primary_fields = (self.config.get("table_primary_fields") or {}).get(stream_name)
        self.client = AirtableClient(
            self.config["token"], self.config["base_id"], table_mapping[stream_name], primary_fields
        )
        self.fields_mapping: dict[str, str] = self.config.get("table_fields_mapping", {}).get(stream_name, {})

    @property
    def max_size(self) -> int:
        return 10  # this is hard-coded due to Airtable's API limitations

    def _preprocess_record(self, record: dict[str, Any]) -> dict[str, Any]:
        fields = list(record.keys())
        cleaned: dict[str, Any] = {}
        for key in fields:
            mapped_key = self.fields_mapping.get(key, key)
            if mapped_key == "__NULL__":
                continue
            value = record[key]
            if isinstance(value, dict):
                cleaned[mapped_key] = self._preprocess_record(value)
            elif isinstance(value, datetime.datetime):
                cleaned[mapped_key] = value.isoformat()
            elif isinstance(value, Decimal):
                cleaned[mapped_key] = float(value)
            else:
                cleaned[mapped_key] = value
        return cleaned

    def start_batch(self, context: dict[str, Any]) -> None:
        """Start a batch."""
        logger.debug("Starting batch '%s' for stream '%s'", context.get("batch_id"), self.stream_name)
        self.current_batch = []

    def process_record(self, record: dict[str, Any], context: dict[str, Any]) -> None:
        """Process the record."""
        self.current_batch.append(self._preprocess_record(record))

    def process_batch(self, context: dict[str, Any]) -> None:
        """Write out any prepped records and return once fully written."""
        self.client.upsert_batch(self.current_batch, self.config["destructive"])
