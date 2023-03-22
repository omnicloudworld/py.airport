import json as _json
from ._terminal import _TerminalDict


# make parameters dictionary from mixed kwargs argument
def _enrich_dict(target: dict, src: dict, key: str, default=None) -> dict:
    if key in src:
        target[key] = src[key]
    elif default is not None:
        target[key] = default
    return target


# parameters for open() excluding "mode" and "encoding"
open_params = ['buffering', "errors", "newline", "closefd", "opener"]


class LocalJSON(_TerminalDict.Gate):

    @classmethod
    def arriving(cls, place: str, **options):

        open_kwargs = {}  # it is important because the open() function doesn't contains **kwargs
        open_kwargs = _enrich_dict(open_kwargs, options, "mode", "r")
        open_kwargs = _enrich_dict(open_kwargs, options, "encoding", "utf-8")
        for k in open_params:
            open_kwargs = _enrich_dict(open_kwargs, options, k)

        with open(place, **open_kwargs) as json_file:  # pylint: disable=unspecified-encoding
            return _json.load(json_file, **options)

    @classmethod
    def departure(cls, parcel, place: str, **options):

        open_kwargs = {}  # it is important because the open() function doesn't contains **kwargs
        open_kwargs = _enrich_dict(open_kwargs, options, "mode", "w")
        open_kwargs = _enrich_dict(open_kwargs, options, "encoding", "utf-8")
        for k in open_params:
            open_kwargs = _enrich_dict(open_kwargs, options, k)

        with open(place, **open_kwargs) as json_file:  # pylint: disable=unspecified-encoding
            _json.dump(parcel, json_file, **options)
