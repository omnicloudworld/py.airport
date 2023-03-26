
from os import path as path

from ...tools.pkg import recursive_import

# Import all submodules of current package. This is done to make sure that
# all third-party Gates are imported and registered.
package_path = path.dirname(path.abspath(__file__))
recursive_import(__name__, package_path)
