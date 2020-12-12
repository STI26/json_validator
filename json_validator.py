from util import get_json, get_type, get_list_of_path


json_schemas = {}

problem_descriptions = {
    'schema_not_found': {
        'problem': 'Проверить корректность данных не представляется возможным ввиду отсутствия схемы к json файлу.',
        'resolve': 'Добавьте используемую схему.'
    },
    'not_dict': {
        'problem': 'Текущий файл не содержит ожидаемый тип данных.',
        'resolve': 'Измените тип данных на "словарь"(ключ - значение).'
    },
    'fields_missing': {
        'problem': 'Отсутствуют обязательные поля: {}.',
        'resolve': 'Добавьте отсутствующие поля.'
    },
    'invalid_fields': {
        'problem': 'Следующие поля не содержит ожидаемый тип данных: {}.',
        'resolve': 'Измените тип данных на указанный.'
    },
}


def main():
    schema_paths = get_list_of_path('./task_folder/schema', '.schema')
    load_schemas(schema_paths)
    event_paths = get_list_of_path('./task_folder/event', '.json')
    check_events(event_paths)


def check_events(event_paths):
    f = open('README.txt', 'w')
    fail_count = 0
    for name, path in event_paths.items():
        obj = get_json(path)
        message = test_event(obj)
        if not message.get("result"):
            fail_count += 1
            f.write(f'Имя файла: {name}.json\n')
            f.write(f'Результат проверки: {message.get("result")}\n')
            f.write(f'Схема: {message.get("schema")}\n')
            p_count = 0
            for problem in message.get("problems"):
                p_count += 1
                f.write(f'  Проблема #{p_count}: {problem.get("problem")}\n')
                f.write(f'  Решение #{p_count}: {problem.get("resolve")}\n\n')

    f.write(f'Результат: в {fail_count} из {len(event_paths)} файлов найдены ошибки.\n\n')
    f.close()


def test_event(obj):
    message = {
        'result': True,
        'problems': [],
        'type': type(obj)
    }

    # Checking type
    if not isinstance(obj, dict) or obj is None:
        message['problems'].append(problem_descriptions.get('not_dict'))
        message['result'] = False
        return message

    # Get json schema
    event = obj.get('event', 'Схема отсутствует.')
    message['schema'] = event

    # Сhecking for schema presence
    try:
        schema = json_schemas[event]
    except KeyError:
        message['problems'].append(
            problem_descriptions.get('schema_not_found')
        )
        message['result'] = False
        return message

    err = check_fields(obj, schema)
    if err.get('fields_missing'):
        message['result'] = False
        problem = problem_descriptions.get('fields_missing').copy()
        fields = ', '.join(err['fields_missing'])
        problem['problem'] = problem['problem'].format(fields)
        message['problems'].append(problem)

    if err.get('invalid_fields'):
        message['result'] = False
        problem = problem_descriptions.get('invalid_fields').copy()
        template = '{}(ожидаемый тип: {}; текущий: {})'
        fields_list = []

        for field in err['invalid_fields']:
            fields_list.append(template.format(
                field['field'],
                field['correct_type'],
                field['current_type']
            ))

        fields = ', '.join(fields_list)
        problem['problem'] = problem['problem'].format(fields)
        message['problems'].append(problem)

    return message


def check_fields(target, schema):
    errors = {
        'fields_missing': [],
        'invalid_fields': []
    }

    obj_type = schema.get('type')
    # Check type
    is_correct_type = isinstance(target, get_type(obj_type))
    if not is_correct_type:
        return {'correct_type': obj_type, 'current_type': type(target)}

    elif obj_type == 'object':
        # Check required fields
        for field in schema.get('required'):
            if field.strip() not in target.keys():
                errors['fields_missing'].append(field)

        # Check all fields
        for key, val in schema.get('properties').items():
            if target.get(key):
                res = check_fields(target[key], val)

                if res.get('correct_type'):
                    res['field'] = key
                    errors['invalid_fields'].append(res)
                else:
                    errors['fields_missing'].extend(res['fields_missing'])
                    errors['invalid_fields'].extend(res['invalid_fields'])

    elif obj_type == 'array':
        # Check items
        if schema.get('items'):
            for item in target:
                res = check_fields(item, schema['items'])

                if res.get('correct_type'):
                    res['field'] = key
                    errors['invalid_fields'].append(res)
                else:
                    errors['fields_missing'].extend(res['fields_missing'])
                    errors['invalid_fields'].extend(res['invalid_fields'])

    return errors


def load_schemas(list_of_path):
    for k, v in list_of_path.items():
        json_schemas[k] = get_json(v)


if __name__ == '__main__':
    main()
