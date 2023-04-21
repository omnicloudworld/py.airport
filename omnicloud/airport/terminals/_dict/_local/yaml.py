from os import makedirs, path

import yaml

from ....abc import Gate
from ....tools.files import kw4open, parameters as parameters4files
from ....tools.yaml import kw4yaml_safedump, kw4yaml_safeload, parameters as parameters4yaml

__all__ = ['LocalYAML']


class LocalYAML(Gate):

    @property
    def parameters(self) -> dict:
        return {'files': parameters4files, 'yaml': parameters4yaml}

    @classmethod
    def arriving(cls, place: str, **options) -> dict | list:

        open_kwargs = kw4open(options, "r", name4log=cls.__name__)
        yaml_kwargs = kw4yaml_safeload(options, name4log=cls.__name__)

        with open(place, **open_kwargs) as yaml_file:  # pylint: disable=unspecified-encoding
            return yaml.safe_load(yaml_file, **yaml_kwargs)

    @classmethod
    def departure(cls, parcel, place: str, **options) -> None:

        open_kwargs = kw4open(options, "w", name4log=cls.__name__)
        yaml_kwargs = kw4yaml_safedump(options, name4log=cls.__name__)

        if not path.exists(path.dirname(place)):
            makedirs(path.dirname(place))

        with open(place, **open_kwargs) as yaml_file:  # pylint: disable=unspecified-encoding
            yaml.safe_dump(dict(parcel), yaml_file, **yaml_kwargs)
