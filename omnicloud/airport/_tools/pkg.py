import importlib as _importlib
import pkgutil as _pkgutil
from os import path as _path


def _recursive_import(package_name, path):

    for module_info in _pkgutil.iter_modules([path]):
        module_name = f"{package_name}.{module_info.name}"
        _importlib.import_module(module_name)
        module_path = _path.join(path, module_info.name)

        if _path.isdir(module_path):
            _recursive_import(module_name, module_path)
