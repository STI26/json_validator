from typing import List


class Report(object):
    def __init__(self, file_name: str):

        self.file_name = file_name
        self.schema_name: str = ''
        self.errors: List[str] = []
        self._status = False

    def __str__(self):
        errors = "; ".join(self.errors)
        return f'file: {self.file_name}\n' \
               f'status: {self.status}\n' \
               f'schema: {self.schema_name}\n' \
               f'errors: {errors}\n'

    @property
    def status(self):
        return 'Valid' if self._status else 'Invalid'

    @status.setter
    def status(self, status: bool):
        self._status = bool(status)

    def add_error(self, text: str):
        if isinstance(text, str):
            self.errors.append(text)
        else:
            raise 'Incorrect type! Type of the variable must be a string.'
