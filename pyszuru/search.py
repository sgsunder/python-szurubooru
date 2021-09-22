from typing import List, Generator
import warnings

from collections import namedtuple
from contextlib import nullcontext

from tqdm import tqdm

from .api import API, FileToken
from .resource import Resource
from .tag import Tag
from .post import Post


SearchResult = namedtuple("SearchResult", ["post", "distance", "exact"], defaults=[False])


def _search_generic(
    api: API,
    search_query: str,
    transforming_class: type,
    page_size: int,
    show_progress_bar: bool = False,
) -> Generator[Resource, None, None]:
    offset = 0
    total = None
    with (tqdm() if show_progress_bar else nullcontext()) as pbar:
        while True:
            page = api._call(
                "GET",
                transforming_class._get_class_urlparts(),
                urlquery={"offset": offset, "limit": page_size, "query": search_query},
            )
            offset = offset + len(page["results"])
            if page["total"] != total:
                total = page["total"]
                if show_progress_bar:
                    pbar.total = total
                    pbar.refresh()
            for item in page["results"]:
                if show_progress_bar:
                    pbar.update()
                yield transforming_class(api, item)
            if offset >= total:
                break


def search_tag(
    api: API, search_query: str, page_size: int = 20, show_progress_bar: bool = False
) -> Generator[Tag, None, None]:
    warnings.warn(
        "search_tag() is deprecated, use API.search_tag() instead", DeprecationWarning
    )
    return _search_generic(api, search_query, Tag, page_size, show_progress_bar)


def search_post(
    api: API, search_query: str, page_size: int = 20, show_progress_bar: bool = False
) -> Generator[Post, None, None]:
    warnings.warn(
        "search_post() is deprecated, use API.search_post() instead", DeprecationWarning
    )
    return _search_generic(api, search_query, Post, page_size, show_progress_bar)


def search_by_image(api: API, image: FileToken) -> List[SearchResult]:
    warnings.warn(
        "search_by_image() is deprecated, use API.search_by_image() instead",
        DeprecationWarning,
    )
    result = api._call(
        "POST", ["posts", "reverse-search"], body={"contentToken": image.token}
    )
    ret = [
        SearchResult(post=Post(api, x["post"]), distance=x["distance"])
        for x in result["similarPosts"]
    ]
    if result["exactPost"]:
        ret.insert(
            0, SearchResult(post=Post(api, result["exactPost"]), distance=None, exact=True)
        )
    return ret
