from pathlib import Path
import json


class BaseFileInstance(object):
    """
    BaseFileInstance.

    args:
    - path: path to directory or file.
    - suffix: extension of required files.
    - include_subdir: include all subdirectories, recursively.
    """

    def __init__(self, path: str, suffix: str = None,
                 include_subdir: bool = False):
        self.path = path
        self.suffix = suffix
        self.include_subdir = include_subdir
        self.files = self._get_files()

    def _get_files(self):
        """
        Get all files in a directory with the `self.suffix`.
        """

        obj = Path(self.path)

        if not obj.exists():
            return None

        if obj.is_file():
            return {self._get_file_name(obj): obj}

        if obj.is_dir():
            if self.include_subdir:
                pattern = '**/*.{}'
                dict_key = self._get_str_path
            else:
                pattern = '*.{}'
                dict_key = self._get_file_name

            path_list = obj.glob(pattern.format(self.suffix))
            return {dict_key(i): i for i in path_list}

        return None

    def _get_str_path(self, path: Path):
        return str(path)

    def _get_file_name(self, path: Path):
        return path.stem

    def load_file(self, path: Path):
        """
        Load JSON from file.
        """

        with open(path) as f:
            return json.load(f)

        return None


class SchemaInstance(BaseFileInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schemas = {}

    def get_schema(self, schema_name: str):
        if schema_name in self._schemas:
            return self._schemas[schema_name]

        if schema_name not in self.files:
            return None

        schema = self.load_file(self.files[schema_name])

        # Update schemas
        self._schemas[schema_name] = schema

        return schema


class JsonInstance(BaseFileInstance):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def generator(self):
        for file in self.files.values():
            yield (self.load_file(file), str(file))
