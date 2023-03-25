import importlib as _importlib
import pkgutil as _pkgutil
from os import path as _path

__all__ = [
    'recursive_import',
    'abstract_checker'
]


def recursive_import(package_name, path):

    for module_info in _pkgutil.iter_modules([path]):
        module_name = f"{package_name}.{module_info.name}"
        _importlib.import_module(module_name)
        module_path = _path.join(path, module_info.name)

        if _path.isdir(module_path):
            recursive_import(module_name, module_path)


def abstract_checker(cls, attr_name: str) -> None:
    attr = getattr(cls, attr_name)
    if hasattr(attr, '__isabstractmethod__') and attr.__isabstractmethod__:
        raise NotImplementedError(
            f'The attribute "{cls.__name__}.{attr_name}" is required. Please read documentation of ZZZ!!'
        )
