import jsonschema

from jsonschema import validate

JSON_UPDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "tenant": {"type": "string"},
        "ipaddresses": {"type": "array"},
    },
    "required": ["tenant", "ipaddresses"]
}


def validate_json(json_data, json_schema):
    '''Validate JSON data based on JSON schema

    Parameters
    ----------
    json_data : obj
        Any JSON object,
    json_schema : dict
        Dict that describes what kind of json you expect,
    
    Raises
    ------
    None

    Returns
    -------
    True if JSON data is valid based on schema
    False if JSON data is not valid based on schema
    '''
    try:
        validate(instance=json_data, schema=json_schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True

