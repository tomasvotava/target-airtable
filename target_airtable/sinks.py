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
        stream_settings: dict[str, Any] = self.config.get("streams", {}).get(stream_name, {})
        self.destructive = stream_settings.get("destructive", False)
        self.upsert = stream_settings.get("upsert", False)
        table_id = stream_settings.get("table_id")
        if not table_id:
            logger.warning(f"Stream {stream_name!r} has no table id set. Its name will be used.")
            table_id = stream_name
        match_fields = stream_settings.get("match_fields")
        if not self.upsert and match_fields:
            logger.warning(f"Stream {stream_name!r} has upsert = false, match fields will be ignored.")
            match_fields = None
        self.client = AirtableClient(self.config["token"], self.config["base_id"], table_id, match_fields)
        self.fields_mapping: dict[str, str] = stream_settings.get("fields_mapping", {})

    @property
    def max_size(self) -> int:
        return 10  # this is hard-coded due to Airtable's API limitations

    def _preprocess_record(self, record: dict[str, Any], *, remap: bool = True) -> dict[str, Any]:
        fields = list(record.keys())
        cleaned: dict[str, Any] = {}
        for key in fields:
            mapped_key = key
            if remap:
                mapped_key = self.fields_mapping.get(key, key)
                if mapped_key == "__NULL__":
                    continue
            value = record[key]
            if isinstance(value, dict):
                cleaned[mapped_key] = self._preprocess_record(value, remap=False)  # do not remap nested fields
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
        if self.upsert:
            self.client.upsert_batch(self.current_batch, self.destructive)
        else:
            if self.destructive:
                logger.warning(
                    f"Cannot perform destructive insert for stream {self.stream_name!r}, "
                    "only upserts may be destructive."
                )
            self.client.insert_batch(self.current_batch)
