from __future__ import annotations
from typing import Any, Dict, List, Callable

from pyszuru.api import API, FileToken
from pyszuru.resource import Resource
from pyszuru.tag import Tag


class Post(Resource):
    @staticmethod
    def _validate_safety(safety: str) -> None:
        if safety not in ("safe", "sketchy", "unsafe"):
            raise ValueError("Safety must be of value safe, sketchy, or unsafe")

    # Implementing Abstract Methods
    def _get_instance_urlparts(self) -> List[str]:
        return ["post", str(self._json["id"])]

    @classmethod
    def _get_class_urlparts(cls) -> List[str]:
        return ["posts"]

    def _setter_transforms(self) -> Dict[str, Callable]:
        return {
            "tags": lambda x: {"names": x.names, "category": x.category},
            "relations": lambda x: {"id": x.id_},
        }

    def _getter_transforms(self) -> Dict[str, Callable]:
        return {
            "tags": lambda x: Tag(self._api, x),
            "relations": lambda x: Post(self._api, x),
        }

    def _serialized(self) -> Dict[str, Any]:
        ret = self._copy_new_json(
            ["tags", "safety", "source", "relations", "flags", "contentToken", "thumbnailToken"]
        )
        if "tags" in ret:
            ret["tags"] = [tag["names"][0] for tag in ret["tags"]]
        if "relations" in ret:
            ret["relations"] = [post["id"] for post in ret["relations"]]
        return ret

    # Factory Methods
    @classmethod
    def from_id(cls, api: API, id_: int) -> Post:
        p = cls(api, {"id": id_})
        p.pull()
        return p

    @classmethod
    def new(cls, api: API, content: FileToken, safety: str) -> Post:
        cls._validate_safety(safety)
        p = cls(api, {})
        p._json_new = {
            "tags": [],
            "safety": safety,
            "contentToken": content.token,
        }
        p.push()
        return p

    # Getters and Setters
    @property
    def id_(self) -> int:
        return self._generic_getter("id")

    @id_.setter
    def id_(self, val: int) -> None:
        self._generic_setter("id", val)

    @property
    def safety(self) -> str:
        return self._generic_getter("safety")

    @safety.setter
    def safety(self, val: str) -> None:
        self._validate_safety(val)
        self._generic_setter("safety", val)

    @property
    def source(self) -> List[str]:
        return self._generic_getter("source").splitlines()

    @source.setter
    def source(self, val: List[str]) -> None:
        self._generic_setter("source", "\n".join(val))

    @property
    def tags(self) -> List[Tag]:
        return self._generic_getter("tags")

    @tags.setter
    def tags(self, val: List[Tag]) -> None:
        self._generic_setter("tags", val)

    @property
    def relations(self) -> List[Post]:
        return self._generic_getter("relations")

    @relations.setter
    def relations(self, val: List[Post]) -> None:
        self._generic_setter("relations", val)

    @property
    def content(self) -> str:
        return self._file_getter("content")

    @content.setter
    def content(self, val: FileToken):
        self._file_setter("content", val)

    @property
    def thumbnail(self) -> str:
        return self._file_getter("thumbnail")

    @thumbnail.setter
    def thumbnail(self, val: FileToken):
        self._file_setter("thumbnail", val)

    @property
    def type_(self) -> str:
        return self._generic_getter("type")

    @property
    def mime(self) -> str:
        return self._generic_getter("mimeType")

    @property
    def width(self) -> int:
        return self._generic_getter("canvasWidth")

    @property
    def height(self) -> int:
        return self._generic_getter("canvasHeight")

    # Flag Getters and Setters
    def _flag_getter(self, flag_name: str) -> bool:
        flag_list = self._generic_getter("flags")
        return flag_name in flag_list

    def _flag_setter(self, flag_name: str, val: bool) -> None:
        flag_list = self._generic_getter("flags")
        if val:
            if flag_name not in flag_list:
                flag_list.append(flag_name)
        else:
            if flag_name in flag_list:
                flag_list.remove(flag_name)
        self._generic_setter("flags", flag_list, False)

    @property
    def loop(self) -> bool:
        return self._flag_getter("loop")

    @loop.setter
    def loop(self, val: bool) -> None:
        self._flag_setter("loop", val)

    @property
    def sound(self) -> bool:
        return self._flag_getter("sound")

    @sound.setter
    def sound(self, val: bool) -> None:
        self._flag_setter("sound", val)
