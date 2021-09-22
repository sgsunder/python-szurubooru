from __future__ import annotations
from typing import List, Generator

from .api import API as _API, FileToken, SzurubooruHTTPError
from .resource import Resource, ResourceNotSynchronized
from .post import Post, PostNote
from .tag import Tag
from .search import search_tag, search_post, search_by_image, _search_generic, SearchResult


class API(_API):
    def getPost(self, id_: int) -> Post:
        p = Post(self, {"id": id_})
        p.pull()
        return p

    def createPost(self, content: FileToken, safety: str) -> Post:
        Post._validate_safety(safety)
        p = Post(self, {})
        p._json_new = {
            "tags": [],
            "safety": safety,
            "contentToken": content.token,
        }
        p.push()
        return p

    def getTag(self, id_: str) -> Tag:
        t = Tag(self, {"names": [id_]})
        t.pull()
        return t

    def createTag(self, name: str) -> Tag:
        # Get default tag category
        tag_cats = [
            x["name"]
            for x in self._call("GET", ["tag-categories"])["results"]
            if x["default"]
        ]
        assert len(tag_cats) == 1
        default_cat = tag_cats[0]
        # Create and return tag
        t = Tag(self, {})
        t._json_new = {"names": [name], "category": default_cat}
        t.push()
        return t

    def search_tag(  # noqa: F811
        self, search_query: str, page_size: int = 20, show_progress_bar: bool = False
    ) -> Generator[Tag, None, None]:
        return _search_generic(self, search_query, Tag, page_size, show_progress_bar)

    def search_post(  # noqa: F811
        self, search_query: str, page_size: int = 20, show_progress_bar: bool = False
    ) -> Generator[Post, None, None]:
        return _search_generic(self, search_query, Post, page_size, show_progress_bar)

    def search_by_image(self, image: FileToken) -> List[SearchResult]:  # noqa: F811
        result = self._call(
            "POST", ["posts", "reverse-search"], body={"contentToken": image.token}
        )
        ret = [
            SearchResult(post=Post(self, x["post"]), distance=x["distance"])
            for x in result["similarPosts"]
        ]
        if result["exactPost"]:
            ret.insert(
                0,
                SearchResult(
                    post=Post(self, result["exactPost"]), distance=None, exact=True
                ),
            )
        return ret
