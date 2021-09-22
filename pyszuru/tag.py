from __future__ import annotations
from typing import Any, Dict, List, Callable
import warnings

from .api import API
from .resource import Resource, ResourceNotSynchronized


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
        ret = self._copy_new_json(
            ["names", "category", "description", "implications", "suggestions"]
        )
        if "implications" in ret:
            ret["implications"] = [x["names"][0] for x in ret["implications"]]
        if "suggestions" in ret:
            ret["suggestions"] = [x["names"][0] for x in ret["suggestions"]]
        return ret

    # Factory Methods
    @classmethod
    def from_id(cls, api: API, id_: str) -> Tag:
        warnings.warn(
            "Tag.from_id() is deprecated, use API.getTag() instead", DeprecationWarning
        )
        t = cls(api, {"names": [id_]})
        t.pull()
        return t

    @classmethod
    def new(cls, api: API, name: str) -> Tag:
        warnings.warn(
            "Tag.new() is deprecated, use API.createTag() instead", DeprecationWarning
        )
        # Get default tag category
        tag_cats = [
            x["name"]
            for x in api._call("GET", ["tag-categories"])["results"]
            if x["default"]
        ]
        assert len(tag_cats) == 1
        default_cat = tag_cats[0]
        # Create and return tag
        t = cls(api, {})
        t._json_new = {"names": [name], "category": default_cat}
        t.push()
        return t

    def merge_from(self, source: Tag, add_as_alias: bool) -> None:
        """
        Merges source tag into this tag
        """
        if "version" not in source._json or source._json_new:
            raise ResourceNotSynchronized("Target tag is not synchronized")
        if "version" not in self._json or self._json_new:
            raise ResourceNotSynchronized("This tag is not synchronized")
        data = self._api._call(
            "POST",
            ["tag-merge"],
            body={
                "removeVersion": source._json["version"],
                "remove": source.primary_name,
                "mergeToVersion": self._json["version"],
                "mergeTo": self.primary_name,
            },
        )
        self._update_json(data, force=True)
        if add_as_alias:
            n = self.names
            n.extend([x for x in source._json["names"] if x not in n])
            self.names = n
            self.push()
        source._json = {}

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
    def primary_name(self) -> str:
        return self.names[0]

    @primary_name.setter
    def primary_name(self, val: str) -> None:
        existing_names = self.names
        if val in existing_names:
            existing_names.remove(val)
        existing_names.insert(0, val)
        self.names = existing_names

    def add_name(self, val: str) -> None:
        existing_names = self.names
        if val not in existing_names:
            existing_names.append(val)
        self.names = existing_names

    def __str__(self) -> str:
        return self.primary_name

    def __repr__(self) -> str:
        return f"{self._api!r}.<Tag of name '{self.primary_name}'>"
