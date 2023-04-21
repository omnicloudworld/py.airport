from .dict import enrich as _enrich
from .dict import item_converter as _converter

__all__ = [
    'parameters',
    'kw4yaml_safeload',
    'kw4yaml_safedump'
]

parameters = {
    'safeload': [
    ],
    'safedump': [
        'default_style',
        'default_flow_style',
        'sort_keys',
        'indent',
        'width',
        'canonical',
        'allow_unicode',
        'line_break',
        'encoding',
        'explicit_start',
        'explicit_end',
        'version',
        'tags'
    ]
}


def kw4yaml_safeload(options: dict, name4log: str | None = None) -> dict:

    if not name4log:
        name4log = kw4yaml_safeload.__name__

    kwargs = {}
    for k in parameters['safeload']:
        kwargs = _enrich(kwargs, options, k)

    return kwargs


def kw4yaml_safedump(options: dict, name4log: str | None = None) -> dict:

    if not name4log:
        name4log = kw4yaml_safedump.__name__

    kwargs = {}
    for k in parameters['safedump']:
        kwargs = _enrich(kwargs, options, k)

    kwargs = _converter(kwargs, "default_flow_style", bool, name4log)
    kwargs = _converter(kwargs, "sort_keys", bool, name4log)
    kwargs = _converter(kwargs, "indent", int, name4log)
    kwargs = _converter(kwargs, "width", int, name4log)
    kwargs = _converter(kwargs, "canonical", bool, name4log)

    return kwargs
