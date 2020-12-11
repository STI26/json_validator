import os
import functools
import json


def get_type(t):
    json_types = {
        'string': (str,),
        'number': (int, float,),
        'integer': (int,),
        'object': (dict,),
        'array': (list,),
        'boolean': (bool,),
        'null': (None,)
    }
    if isinstance(t, list):
        return functools.reduce(lambda a, b: a+b, [json_types[i] for i in t])
    else:
        return json_types[t]


def get_json(path):
    with open(path, 'r') as f:
        return json.load(f)
    return None


def get_list_of_path(path, file_type):
    list_of_path = {}

    with os.scandir(path) as it:
        for entry in it:
            if entry.name.endswith(file_type) and entry.is_file():
                list_of_path[entry.name[:-7]] = entry.path

    return list_of_path
