from typing import Generator, List

from .api import API as _API
from .api import FileToken, SzurubooruHTTPError
from .pool import Pool
from .post import Post, PostNote
from .resource import Resource, ResourceNotSynchronized
from .search import (
    SearchResult,
    _search_generic,
    search_by_image,
    search_post,
    search_tag,
)
from .tag import Tag


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
        if not isinstance(name, str):
            raise ValueError("Tag name must be a string")

        # Get default tag category
        tag_cats = self._call("GET", ["tag-categories"])["results"]
        default_cat = [x for x in tag_cats if x["default"]]
        assert len(default_cat) == 1
        default_cat = default_cat[0]["name"]

        # Create and return tag
        t = Tag(self, {})
        t._json_new = {"names": [name], "category": default_cat}
        t.push()
        return t

    def getPool(self, id_: int) -> Pool:
        p = Pool(self, {"id": id_})
        p.pull()
        return p

    def createPool(self, name: str) -> Pool:
        if not isinstance(name, str):
            raise ValueError("Pool name must be a string")

        # Get default pool category
        tag_cats = self._call("GET", ["pool-categories"])["results"]
        default_cat = [x for x in tag_cats if x["default"]]
        assert len(default_cat) == 1
        default_cat = default_cat[0]["name"]

        p = Pool(self, {})
        p._json_new = {
            "names": [name],
            "category": default_cat,
        }

        # For some reason, the API uses POST /pool instead of POST /pools,
        # which is inconsistent with the other resources.
        # Monkey patch Pool._get_class_urlparts method to fix this until it is patched
        # in the API.
        _unmonkeypatch = p._get_class_urlparts
        try:
            p._get_class_urlparts = lambda: ["pool"]
            p.push()
        finally:
            p._get_class_urlparts = _unmonkeypatch
        return p

    def search_tag(  # noqa: F811
        self,
        search_query: str,
        page_size: int = 20,
        show_progress_bar: bool = False,
        eager_load: bool = False,
    ) -> Generator[Tag, None, None]:
        return _search_generic(
            self, search_query, Tag, page_size, show_progress_bar, eager_load
        )

    def search_post(  # noqa: F811
        self,
        search_query: str,
        page_size: int = 20,
        show_progress_bar: bool = False,
        eager_load: bool = False,
    ) -> Generator[Post, None, None]:
        return _search_generic(
            self, search_query, Post, page_size, show_progress_bar, eager_load
        )

    def search_pool(  # noqa: F811
        self,
        search_query: str,
        page_size: int = 20,
        show_progress_bar: bool = False,
        eager_load: bool = False,
    ) -> Generator[Pool, None, None]:
        return _search_generic(
            self, search_query, Pool, page_size, show_progress_bar, eager_load
        )

    def search_by_image(self, image: FileToken) -> List[SearchResult]:  # noqa: F811
        result = self._call(
            "POST", ["posts", "reverse-search"], body={"contentToken": image.token}
        )
        ret = [
            SearchResult(post=Post(self, x["post"]), distance=x["distance"], exact=False)
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
