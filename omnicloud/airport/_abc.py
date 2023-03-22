from __future__ import annotations

import json
from abc import ABC, ABCMeta, abstractmethod
from os import environ as env
from typing import Any


def abstract_checker(cls, attr_name: str) -> None:
    attr = getattr(cls, attr_name)
    if hasattr(attr, '__isabstractmethod__') and attr.__isabstractmethod__:
        raise NotImplementedError(
            f'The attribute "{cls.__name__}.{attr_name}" is required. Please read documentation of ZZZ!!'
        )


class Gate(ABC, metaclass=ABCMeta):

    def __init_subclass__(cls, **kw):
        abstract_checker(cls, 'arriving')
        abstract_checker(cls, 'departure')
        super().__init_subclass__(**kw)

    def __init__(self, **kw):
        super().__init__(**kw)

    @classmethod
    @abstractmethod
    def arriving(cls, place: str, **options):
        ...

    @classmethod
    @abstractmethod
    def departure(cls, parcel, place: str, **options):
        ...


class Building(ABC):

    def __init_subclass__(cls, **kw):
        abstract_checker(cls, 'parcel')
        super().__init_subclass__(**kw)

    def __init__(self, **kw):
        super().__init__(**kw)

    Gate = Gate

    @property
    @abstractmethod
    def parcel(self):
        ...

    @classmethod
    def arriving(cls, waybill: dict[str, Any] | str):
        gate, place, options = cls.waybill_reader(waybill)
        return gate.arriving(place, **options) if options else gate.arriving(place)

    def departure(self, waybill: dict[str, Any] | str):
        gate, place, options = self.waybill_reader(waybill)
        return gate.departure(self.parcel, place, **options) if options else gate.departure(self.parcel, place)  # pylint: disable=line-too-long

    @classmethod
    def waybill_reader(cls, path: dict | str) -> tuple[Gate, str, dict[str, Any] | None]:

        path_dic: dict = json.loads(path) if isinstance(path, str) else path

        if 'gate' not in path_dic or path_dic['gate'] == '':
            raise ValueError("gate is required property in path")

        if 'place' not in path_dic or path_dic['place'] == '':
            raise ValueError("place is required property in path")

        # Extract required properties from path dict
        gate_name: str = str(path_dic.get("gate"))
        place_str: str = str(path_dic.get("place"))

        # Find the door class based on door_name
        gate_class: Gate | None = None
        for sub_cls in cls.Gate.__subclasses__():
            if sub_cls.__qualname__ == gate_name:
                gate_class = sub_cls  # type: ignore
                break

        if not gate_class:
            raise ValueError(f"No Gate class found for gate name: {gate_name}")

        # Fix and extract params, if available
        params = path_dic.get("params", None)

        if params:
            fixed_params = {}
            for key, value in params.items():
                if isinstance(key, str):
                    if key.startswith("$"):
                        env_var_name = f'GATE_{key[1:].upper()}'
                        if env_var_name in env:
                            fixed_params[key[1:]] = env[env_var_name]
                        else:
                            fixed_params[key[1:]] = value
                        del fixed_params[key]
                    else:
                        fixed_params[key] = value
        else:
            fixed_params = None

        # Return the extracted values
        return gate_class, place_str, fixed_params
