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
            "table_mapping",
            th.ObjectType(additional_properties=th.StringType),
            description="Mapping of source stream => airtable table id",
            required=True,
        ),
        th.Property(
            "table_primary_fields",
            th.ObjectType(additional_properties=th.ArrayType(th.StringType)),
            description=(
                "A mapping of source stream => list of record primary fields as visible in Airbyte. "
                "Defaults to the internal 'id' for each stream."
            ),
        ),
        th.Property("base_id", th.StringType, description="Airtable base id", required=True),
        th.Property(
            "destructive",
            th.BooleanType,
            description=(
                "If true, fields missing in the source existing "
                "in the destination will be deleted from the destination"
            ),
            default=False,
        ),
        th.Property(
            "table_fields_mapping",
            th.ObjectType(additional_properties=th.ObjectType(additional_properties=th.StringType)),
            description=(
                "An optional mapping of stream_name => {field => renamed_field} to allow renaming "
                "field from streams that do not support stream mapping."
            ),
        ),
    ).to_dict()
    default_sink_class = AirtableSink
