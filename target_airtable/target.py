"""Airtable target class."""

from singer_sdk import typing as th
from singer_sdk.target_base import Target

from target_airtable.sinks import (
    AirtableSink,
)


class TargetAirtable(Target):
    """Singer target for Airtable."""

    name = "target-airtable"
    config_jsonschema = th.PropertiesList(
        th.Property(
            "token", th.StringType, description="The token to authenticate against Airtable API", required=True
        ),
        th.Property(
            "streams",
            th.ObjectType(
                additional_properties=th.ObjectType(
                    th.Property(
                        "destructive",
                        th.BooleanType,
                        description=(
                            "If true, fields missing in the source stream that exist "
                            "in the destination will be deleted from Airtable"
                        ),
                        default=False,
                    ),
                    th.Property(
                        "table_id",
                        th.StringType,
                        nullable=True,
                        default=None,
                        description=(
                            "The Airtable table id this stream should be poured into. "
                            "By default it is expected that the Airtable table name matches the stream name."
                        ),
                    ),
                    th.Property(
                        "upsert",
                        th.BooleanType,
                        default=False,
                        description=(
                            "If true, data from stream will be upserted into the Airtable table. "
                            "Upserted stream must either include `id` field or `match_fields` "
                            "must be set on the stream."
                        ),
                    ),
                    th.Property(
                        "match_fields",
                        th.ArrayType(th.StringType),
                        nullable=True,
                        default=None,
                        description=(
                            "If upserting, list the fields that should act as a primary key for the Airtable table. "
                            "Fields must exist on all records."
                        ),
                    ),
                    th.Property(
                        "fields_mapping",
                        th.ObjectType(additional_properties=th.StringType),
                        nullable=True,
                        default=None,
                        description=(
                            "A primitive fields mapping to be used with taps that do not support stream maps. "
                            "Use `field: __NULL__` to exclude and `old_field: new_field` to rename field."
                        ),
                    ),
                ),
            ),
            description="The configuration for each of the input streams",
            required=False,
        ),
        th.Property("base_id", th.StringType, description="Airtable base id", required=True),
    ).to_dict()
    default_sink_class = AirtableSink
