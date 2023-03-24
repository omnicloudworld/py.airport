from __future__ import annotations

import json
import re
from abc import ABC, ABCMeta, abstractmethod
from base64 import b64decode as b64d
from os import environ as env
from os import path
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
    def arriving(cls, waybill: str, name: str):
        gate, place, options = cls.waybill_reader(waybill, name)
        return gate.arriving(place, **options) if options else gate.arriving(place)

    def departure(self, waybill: str, name: str):
        gate, place, options = self.waybill_reader(waybill, name)
        return gate.departure(self.parcel, place, **options) if options else gate.departure(self.parcel, place)  # pylint: disable=line-too-long

    @classmethod
    def waybill_reader(cls, waybill: str, name: str) -> tuple[Gate, str, dict[str, Any] | None]:

        params = waybill.split("::")
        if len(params) < 2 or len(params) > 3:
            raise ValueError("Invalid waybill format. It should be Gate::Place::Options or Gate::Place")

        gate_name, place, options = params[0], params[1], None

        # Find the door class based on door_name
        gate: Gate | None = None
        for sub_cls in cls.Gate.__subclasses__():
            if sub_cls.__qualname__ == gate_name:
                gate = sub_cls  # type: ignore
                break

        if not gate:
            raise ValueError(f"No Gate class found for gate name: {gate_name}")

        if len(params) == 3:
            param3 = params[2]

            # Check if Param3 has correct format
            def count_cleaned_b64(src: str) -> int:
                return len(re.sub(r'[=]*$', '', src).split('='))

            if not all([count_cleaned_b64(a) > 1 for a in param3.split("||")]):
                raise ValueError(
                    "Invalid Options format. It should be key1=value1||key2=value2||key3=value3"
                )

            # Split key and value properly
            options = {}
            for key_value in param3.split("||"):
                key, value = key_value.split("=", 1)
                options[key] = value      

            # Replace from environment variables
            for key, value in options.items():
                if isinstance(key, str):
                    if key.startswith("$"):
                        env_var_name = f'{gate_name.upper()}_{key[1:].upper()}'
                        if env_var_name in env and env[env_var_name] != '':
                            options[key[1:]] = env[env_var_name]
                        del options[key]

            # Check if any value in Options is base64-encoded
            for key, value in options.items():
                if isinstance(value, str) and value.startswith("b64:"):
                    try:
                        # Decode base64-encoded string
                        decoded_value = b64d(value[4:]).decode()
                        # Convert decoded string to dictionary or list if possible
                        if decoded_value.startswith("[") and decoded_value.endswith("]"):
                            options[key] = json.loads(decoded_value)
                        elif decoded_value.startswith("{") and decoded_value.endswith("}"):
                            options[key] = json.loads(decoded_value)
                        else:
                            options[key] = decoded_value
                    except (ValueError, TypeError):
                        # If decoding or conversion fails, leave the value as-is
                        pass

        # Return the extracted values
        return gate, path.join(place, name), options
