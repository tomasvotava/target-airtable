"""Airtable client."""

import json
import logging
from collections.abc import Iterable
from typing import Any, Optional, TypeVar
from urllib.parse import urljoin

import backoff
import httpx

logger = logging.getLogger(__name__)

AIRTABLE_MAX_BATCH_SIZE = 10
T = TypeVar("T")


def chunkify(iterable: Iterable[T], max_size: int) -> Iterable[list[T]]:
    current = []
    for item in iterable:
        current.append(item)
        if len(current) == max_size:
            yield current
            current = []
    if current:
        yield current


class NonRetryableError(Exception):
    """Error that won't be retried"""


def _format_batch(batch: list[dict[str, Any]], has_id: bool) -> list[dict[str, Any]]:
    formatted: list[dict[str, Any]] = []
    for record in batch:
        field_id = record.pop("id", None)
        if has_id and field_id is None:
            raise ValueError("'id' was expected but the record had none")
        formatted.append({"fields": record, **({"id": field_id} if has_id else {})})
    return formatted


class AirtableClient:
    api_url: str = "https://api.airtable.com/v0/"

    def __init__(self, api_token: str, base_id: str, table_id: str, primary_keys: Optional[list[str]] = None) -> None:
        self.session = httpx.Client(headers={"Authorization": f"Bearer {api_token}"})
        self.base_id = base_id
        self.table_id = table_id
        self.primary_keys = primary_keys or []
        self.endpoint = urljoin(self.api_url, f"{self.base_id}/{self.table_id}")

    @backoff.on_exception(backoff.constant, httpx.HTTPError, max_tries=5, max_time=30)
    def upsert_batch(self, batch: list[dict[str, Any]], destructive: bool = False) -> None:
        if len(batch) > AIRTABLE_MAX_BATCH_SIZE:
            logger.info("Splitting batch of %d", len(batch))
            for chunk in chunkify(batch, AIRTABLE_MAX_BATCH_SIZE):
                self.upsert_batch(chunk, destructive)
            return
        upsert_config = (
            {"fieldsToMergeOn": self.primary_keys} if self.primary_keys else {"fieldsToMergeOn": ["Make", "Model"]}
        )
        method = self.session.put if destructive else self.session.patch
        response = method(
            self.endpoint,
            json={
                "performUpsert": upsert_config,
                "records": _format_batch(batch, has_id=not self.primary_keys),
                "typecast": True,
            },
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            if response.status_code < 500:
                logger.error(
                    "Faulty batch: %s", json.dumps(_format_batch(batch, has_id=not self.primary_keys), default=str)
                )
                raise NonRetryableError(response.text) from error
            raise
