
from .type import convert_to_bool as _convert_to_bool

__all__ = ['enrich_dict', 'type_converter']


# make parameters dictionary from mixed kwargs argument
def enrich_dict(target: dict, src: dict, key: str, default=None) -> dict:
    if key in src:
        target[key] = src[key]
    elif default is not None:
        target[key] = default
    return target


def type_converter(src: dict, key: str, data_type: type, obj: str) -> dict:
    if key in src:
        try:
            src[key] = _convert_to_bool(src[key]) if data_type == bool else data_type(src[key])
        except Exception as ex:
            raise ValueError(
                f'The value "{src[key]}" of the "{key}" parameter in the "{obj}" object is not a valid {data_type.__name__}'  # pylint: disable=line-too-long
            ) from ex
    return src
