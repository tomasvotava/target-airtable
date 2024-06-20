# target-airtable

`target-airtable` is a Singer target for Airtable.

Built with the [Meltano Target SDK](https://sdk.meltano.com).

## Disclaimer

This not meant to be a universal target for Airtable. It is a very specific implementation for a very
specific use case. It is not meant to be a general purpose target for Airtable.

## Installation

### Standalone

```bash
pipx install git+https://github.com/tomasvotava/target-airtable.git
```

### Meltano

Add the target to your Meltano project as a custom target:

```bash
meltano add target target-airtable --from-ref https://raw.githubusercontent.com/tomasvotava/target-airtable/master/target-airtable.yml
```

## Configuration

### Accepted Config Options

| Property | Required | Description |
|:---|:---|:---|
| `token` | Yes | Airtable API token |
| `base_id` | Yes | Airtable base ID |
| `table_mapping` | Yes | Mapping of stream to Airtable table id |
| `table_primary_fields` | No | Mapping of stream to array of Airtable fields that should be used as primary key. If not given, `id` must be present in the records |
| `destructive` | No | If set to `true`, the target will delete all fields that are not present in the stream but are present in Airtable. Default is `false`. |

## Stream maps

Note that you can use stream maps in order to remap individual fields in the stream, e.g. for `tap-faker`:

```yaml
...
plugins:
  extractors:
    - name: tap-faker
      variant: airbyte
      pip_url: git+https://github.com/MeltanoLabs/tap-airbyte-wrapper.git
      config:
        airbyte_config:
          count: 100
        stream_maps:
          products:
            Make: make
            Model: model
            Year: int(year)
            Price: float(price)
            Created at: created_at
            Updated at: updated_at
            make: __NULL__
            model: __NULL__
            year: __NULL__
            price: __NULL__
            created_at: __NULL__
            updated_at: __NULL__
```

See [Inline Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html) in the Meltano SDK documentation for more information.
