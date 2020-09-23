from __future__ import annotations
from typing import Any, Dict, List, Callable

from pyszuru.api import API
from pyszuru.resource import Resource


class Tag(Resource):
    # Implementing Abstract Methods
    def _get_instance_urlparts(self) -> List[str]:
        return ["tag", self._json["names"][0]]

    @classmethod
    def _get_class_urlparts(cls) -> List[str]:
        return ["tags"]

    def _setter_transforms(self) -> Dict[str, Callable]:
        return {
            "implications": lambda x: {"names": x.names, "category": x.category},
            "suggestions": lambda x: {"names": x.names, "category": x.category},
        }

    def _getter_transforms(self) -> Dict[str, Callable]:
        return {
            "implications": lambda x: Tag(self._api, x),
            "suggestions": lambda x: Tag(self._api, x),
        }

    def _serialized(self) -> Dict[str, Any]:
        ret = self._copy_new_json(["names", "category", "description", "implications", "suggestions"])
        if "implications" in ret:
            ret["implications"] = [x.name for x in ret["implications"]]
        if "suggestions" in ret:
            ret["suggestions"] = [x.name for x in ret["suggestions"]]
        return ret

    # Factory Methods
    @classmethod
    def from_name(cls, api: API, name: str) -> Tag:
        t = cls(api, {"names": [name]})
        t.pull()
        return t

    @classmethod
    def new(cls, api: API, name: str) -> Tag:
        # Get default tag category
        tag_cats = [x["name"] for x in api._call("GET", ["tag-categories"])["results"] if x["default"]]
        assert len(tag_cats) == 1
        default_cat = tag_cats[0]
        # Create and return tag
        t = cls(api, {})
        t._json_new = {"names": [name], "category": default_cat}
        t.push()
        return t

    # Getters and Setters
    @property
    def names(self) -> List[str]:
        return self._generic_getter("names")

    @names.setter
    def names(self, val: List[str]) -> None:
        self._generic_setter("names", val)

    @property
    def category(self) -> str:
        return self._generic_getter("category")

    @category.setter
    def category(self, val: str) -> None:
        self._generic_setter("category", val)

    @property
    def implications(self) -> List[Tag]:
        return self._generic_getter("implications")

    @implications.setter
    def implications(self, val: List[Tag]) -> None:
        self._generic_setter("implications", val)

    @property
    def suggestions(self) -> List[Tag]:
        return self._generic_getter("suggestions")

    @suggestions.setter
    def suggestions(self, val: List[Tag]) -> None:
        self._generic_setter("suggestions", val)

    @property
    def description(self) -> str:
        return self._generic_getter("description")

    @description.setter
    def description(self, val: str) -> None:
        self._generic_setter("description", val)

    @property
    def name(self) -> str:
        return self.names[0]
