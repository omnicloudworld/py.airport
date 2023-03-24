
from os import path as _path

from .._tools.pkg import _recursive_import
from ._terminal import _TerminalDict

'''
Import all submodules of current package. This is done to make sure that
all third-party Gates are imported and registered.
'''
_package_path = _path.dirname(_path.abspath(__file__))
_recursive_import(__name__, _package_path)


# Class recreated for provide a more user-friendly namespace and qualified name.
class Terminal(_TerminalDict):
    pass
