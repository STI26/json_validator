#!/usr/bin/env python3
from typing import Union, List
import sys

from libs.file_module import JsonInstance, SchemaInstance
from libs.fields import BaseField, MissingField, IncorrectField
from libs.report import Report
from libs.util import json_type_to_python_type, export_to_html


def validate(target: str, schema: str,
             target_subdir: bool = False,
             schemas_subdir: bool = False,
             field_with_schema_name: str = None) -> Union[None, List[Report]]:
    """
    Validate an instance(s) under a given schema(s).

    args:
    - target can be a directory or a JSON file.
    - schema can be a directory or a SCHEMA file.
    - target_subdir: include all target subdirectories, recursively.
    - schemas_subdir: include all schema subdirectories, recursively.
    - field_with_schema_name: field name in a JSON file
    with schema file name.
    (if the schema is a directory you should specify `field_with_schema_name`)
    """

    reports = []

    schemas = SchemaInstance(schema, 'schema', schemas_subdir)
    objects = JsonInstance(target, 'json', target_subdir)

    for i in (objects, schemas):
        if i.files is None:
            print(f'File or directory "{i.path}" not found.')
            return None

    g = objects.generator()

    for obj, file_name in g:
        report = Report(file_name)

        if field_with_schema_name is None:
            # If didn't set `field_with_schema_name` to use a first schema.
            schema_name = schemas.files.__iter__().__next__()
        else:
            try:
                schema_name = obj[field_with_schema_name]
            except (AttributeError, KeyError, TypeError):
                report.add_error('Schema didn\'t specify.')
                reports.append(report)
                continue

        report.schema_name = schema_name
        schema = schemas.get_schema(schema_name)
        if schema is None:
            report.add_error('Schema didn\'t find.')
            reports.append(report)
            continue

        errors = _validate(obj, schema)

        report.errors = errors
        report.status = not bool(errors)
        reports.append(report)

    return reports


def _validate(target: Union[dict, list], schema: dict) -> List[str]:
    """
    Validate an instance under a given schema.
    """

    report = []

    if not validate_schema(schema):
        report.append('Schema is not valid.')
        return report

    fields_with_error = _validate_field(target, schema)

    [report.append(str(e)) for e in fields_with_error]

    return report


def _validate_field(field: object, schema_field: object) -> List[BaseField]:
    """
    Recursively check fields for:
    - required
    - correct type
    """

    fields_with_error = []

    expected_type = json_type_to_python_type(schema_field.get('type'))
    # Check type
    if not isinstance(field, expected_type):
        fields_with_error.append(
            IncorrectField(name='',
                           real_type=type(field),
                           expected_type=expected_type)
        )

    elif isinstance(field, dict):
        # Check required fields in dict
        for required_field in schema_field.get('required'):
            if required_field not in field.keys():
                fields_with_error.append(
                    MissingField(name=required_field)
                )

        # Check all fields in dict (recursively)
        for key, val in schema_field.get('properties').items():
            if field.get(key):
                errors = _validate_field(field[key], val)

                # Update name fields
                for e in errors:
                    e.add_parent(key)

                # Update fields_with_error
                fields_with_error.extend(errors)

    elif isinstance(field, (list, tuple, set,)):
        # Check items in array
        if schema_field.get('items'):
            for idx, item in enumerate(field):
                errors = _validate_field(item, schema_field['items'])

                # Update name fields
                for e in errors:
                    e.add_parent(f'[{idx}]')

                # Update fields_with_error
                fields_with_error.extend(errors)

    return fields_with_error


def validate_schema(schema: dict) -> bool:
    if not isinstance(schema, dict):
        return False

    for attr in ('type', 'required', 'properties'):
        if attr not in schema.keys():
            return False

    return True


def main(*args, **kwargs):
    report = validate(*args)

    if report is not None:
        export_to_html(report)


if __name__ == '__main__':
    helps = '''
        Run program with args:\n
        python3 {} target schema t_subdir s_subdir field_name
        \nWhere:
        target - directory or a JSON file. (required)
        schema - directory or a SCHEMA file. (required)
        t_subdir - include all target subdirectories.(default: false)
        s_subdir - include all schema subdirectories.(default: false)
        field_name - field name in a JSON file with schema file name.\n
        * if the schema is a directory you should specify `field_name`
    '''

    if len(sys.argv) < 3:
        print(helps.format(sys.argv[0]))
    elif len(sys.argv) > 6:
        err = 'Error: takes from 2 to 5 positional arguments but {} were given'
        print(err.format(len(sys.argv) - 1))
        print(helps.format(sys.argv[0]))
    else:
        if len(sys.argv) > 3:
            sys.argv[3] = True if sys.argv[3] == 'true' else False
        if len(sys.argv) > 4:
            sys.argv[4] = True if sys.argv[4] == 'true' else False

        main(*sys.argv[1:])
