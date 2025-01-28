from typing import Any, Callable, Dict, List

import warnings

from .api import API
from .post import Post
from .resource import Resource, _ResourceList


class Pool(Resource):
    # Implementing Abstract Methods
    def _get_instance_urlparts(self) -> List[str]:
        return ["pool", str(self._json["id"])]

    @classmethod
    def _get_class_urlparts(cls) -> List[str]:
        return ["pools"]

    @classmethod
    def _lazy_load_components(cls) -> List[str]:
        return ["id", "names", "category", "description", "postCount"]

    def _setter_transforms(self) -> Dict[str, Callable]:
        return {
            "posts": lambda x: {"id": x.id_},
        }

    def _getter_transforms(self) -> Dict[str, Callable]:
        return {
            "posts": lambda x: Post(self._api, x),
        }

    def _serialized(self) -> Dict[str, Any]:
        ret = self._copy_new_json(["names", "category", "description", "posts"])
        if "posts" in ret:
            ret["posts"] = [x["id"] for x in ret["posts"]]
        return ret

    # Factory Methods
    @classmethod
    def from_id(cls, api: API, id_: int):  # -> Pool
        warnings.warn(
            "Pool.from_id() is deprecated, use API.getPool() instead", DeprecationWarning
        )
        p = cls(api, {"id": id_})
        p.pull()
        return p

    @classmethod
    def new(
        cls,
        api: API,
        name: "str | List[str]",
        category: str,
    ):
        warnings.warn(
            "Pool.new() is deprecated, use API.createPool() instead", DeprecationWarning
        )
        if name is not None and isinstance(name, str):
            name = [name]
        p = cls(api, {})
        p._json_new = {
            "names": name,
            "category": category,
        }
        p.push()
        return p

    # Getters and Setters
    @property
    def id_(self) -> int:
        return self._generic_getter("id")

    @property
    def names(self) -> List[str]:
        return _ResourceList(
            getter=lambda: self._generic_getter("names"),
            parent_resource=self,
            property_name="names",
        )

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
    def description(self) -> str:
        return self._generic_getter("description")

    @description.setter
    def description(self, val: str) -> None:
        self._generic_setter("description", val)

    @property
    def posts(self) -> List[Post]:
        return _ResourceList(
            getter=lambda: self._generic_getter("posts"),
            parent_resource=self,
            property_name="posts",
        )

    @posts.setter
    def posts(self, val: List[Post]) -> None:
        self._generic_setter("posts", val)

    @property
    def postCount(self) -> int:
        return self._generic_getter("postCount")

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

    def __str__(self) -> str:
        return self.primary_name

    def __repr__(self) -> str:
        return f"{self._api!r}.<Tag of name '{self.primary_name}'>"
