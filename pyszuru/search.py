from typing import List, Generator

from collections import namedtuple

from pyszuru.api import API, FileToken
from pyszuru.resource import Resource
from pyszuru.tag import Tag
from pyszuru.post import Post


SearchResult = namedtuple("SearchResult", ["post", "distance", "exact"], defaults=[False])


def _search_generic(
    api: API, search_query: str, transforming_class: type, page_size: int
) -> Generator[Resource, None, None]:
    offset = 0
    total = None
    while True:
        page = api._call(
            "GET",
            transforming_class._get_class_urlparts(),
            urlquery={"offset": offset, "limit": page_size, "query": search_query},
        )
        for item in page["results"]:
            yield transforming_class(api, item)
        offset = offset + len(page["results"])
        total = page["total"]
        if offset >= total:
            break


def search_tag(api: API, search_query: str, page_size: int = 20) -> Generator[Tag, None, None]:
    return _search_generic(api, search_query, Tag, page_size)


def search_post(api: API, search_query: str, page_size: int = 20) -> Generator[Post, None, None]:
    return _search_generic(api, search_query, Post, page_size)


def search_by_image(api: API, image: FileToken) -> List[SearchResult]:
    result = api._call("POST", ["posts", "reverse-search"], body={"contentToken": image.token})
    ret = [SearchResult(post=Post(api, x["post"]), distance=x["distance"]) for x in result["similarPosts"]]
    if result["exactPost"]:
        ret.insert(0, SearchResult(post=Post(api, result["exactPost"]), distance=None, exact=True))
    return ret
