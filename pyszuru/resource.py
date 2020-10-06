from __future__ import annotations
from typing import Any, Dict, List, Callable

from .api import API, FileToken


class ResourceNotSynchronized(RuntimeError):
    pass


class Resource:
    def __init__(self, api: API, initial_json: Dict[str, Any]):
        self._api = api
        self._json = initial_json
        self._json_new = {}

    # Abstract methods to override
    def _get_instance_urlparts(self) -> List[str]:
        """URL Parts generator for this specific instance"""
        raise NotImplementedError()

    @classmethod
    def _get_class_urlparts(cls) -> List[str]:
        """URL Parts Generator for this class"""
        raise NotImplementedError()

    def _setter_transforms(self) -> Dict[str, Callable]:
        """Converts set value to JSON-serializable dictionary"""
        return {}

    def _getter_transforms(self) -> Dict[str, Callable]:
        """Converts internal JSON dictionary into usable value"""
        return {}

    def _serialized(self) -> Dict[str, Any]:
        """Return formatted JSON dictionary for PUT/POST request body"""
        return {}

    # Common methods
    def _copy_new_json(self, keys_to_copy: List[str]):
        ret = {}
        for key in keys_to_copy:
            if key in self._json_new:
                ret[key] = self._json_new[key]
        return ret

    def _update_json(self, data: Dict[str, Any], force: bool = False):
        if not force:
            for key in data:
                if key not in self._json_new:
                    # property not changed
                    continue
                if self._json[key] == self._json_new[key]:
                    # property set back to original
                    continue
                if data[key] == self._json_new[key]:
                    # property set to new value
                    continue
                raise ResourceNotSynchronized(key)
        self._json_new = {}
        self._json = data

    def pull(self) -> None:
        data = self._api._call("GET", self._get_instance_urlparts())
        self._update_json(data)

    def push(self) -> None:
        body = self._serialized()
        if "version" in self._json and self._json["version"]:
            body["version"] = self._json["version"]
            data = self._api._call("PUT", self._get_instance_urlparts(), body=body)
        else:
            data = self._api._call("POST", self._get_class_urlparts(), body=body)
        self._update_json(data, force=True)

    def synchronized(self) -> bool:
        return bool(self._json_new)

    @classmethod
    def from_id(cls, api: API, id_: Any) -> Resource:
        raise NotImplementedError()

    @classmethod
    def new(cls, api: API, *args, **kwargs) -> Resource:
        raise NotImplementedError()

    @property
    def api(self):
        return self._api

    @classmethod
    def _apply_transforms(
        cls, transforms: Dict[str, Callable], property_name: str, property_value: Any
    ) -> Any:
        if property_value is None:
            return None
        elif isinstance(property_value, list):
            return [
                cls._apply_transforms(transforms, property_name, x) for x in property_value
            ]
        elif property_name in transforms:
            return transforms[property_name](property_value)
        else:
            return property_value

    def _generic_getter(self, property_name: str, dynamic_refresh: bool = True) -> Any:
        if property_name in self._json_new:
            return self._apply_transforms(
                self._getter_transforms(), property_name, self._json_new[property_name]
            )
        elif property_name in self._json:
            return self._apply_transforms(
                self._getter_transforms(), property_name, self._json[property_name]
            )
        elif dynamic_refresh:
            self.pull()
            return self._generic_getter(property_name, False)
        else:
            raise KeyError(f"{property_name} is not present in the JSON response")

    def _generic_setter(
        self, property_name: str, property_value: Any, dynamic_refresh: bool = True
    ) -> None:
        if property_name in self._json:
            if isinstance(self._json[property_name], list):
                if not isinstance(property_value, list):
                    raise ValueError(
                        f"{property_name} must be a list, not {type(property_value)}"
                    )
            self._json_new[property_name] = self._apply_transforms(
                self._setter_transforms(), property_name, property_value
            )
        elif dynamic_refresh:
            self.pull()
            self._generic_setter(property_name, property_value, False)
        else:
            raise KeyError(f"{property_name} is not present in the JSON response")

    def _file_getter(self, property_name: str, dynamic_refresh: bool = True) -> str:
        if f"{property_name}Url" in self._json:
            return self._api._create_data_url(self._json[f"{property_name}Url"])
        elif dynamic_refresh:
            self.pull()
            return self._file_getter(property_name, False)
        else:
            raise KeyError(f"{property_name} is not a URL resource in the JSON response")

    def _file_setter(
        self, property_name: str, property_value: FileToken, dynamic_refresh: bool = False
    ) -> None:
        self._json_new[f"{property_name}Token"] = property_value.token
