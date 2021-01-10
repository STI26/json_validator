class BaseField(object):
    def __init__(self, name: str, *args, **kwargs):
        self.name = name

    def __str__(self):
        return self.name

    def add_parent(self, parent: str):
        if self.name.startswith('['):
            self.name = f'{parent}{self.name}'
        elif self.name:
            self.name = f'{parent}.{self.name}'
        else:
            self.name = parent


class MissingField(BaseField):
    def __str__(self):
        return f'Field "{self.name}" is missing.'


class IncorrectField(BaseField):
    def __init__(self, *args, **kwargs):
        self.real_type: str = None or kwargs.get('real_type')
        self.expected_type: tuple = None or kwargs.get('expected_type')
        super().__init__(*args, **kwargs)

    def __str__(self):
        types = ', '.join([t.__name__ for t in self.expected_type])
        return 'Field "{}" is of type "{}", but expected type(s): {}.'.format(
            self.name, self.real_type.__name__, types
        )
