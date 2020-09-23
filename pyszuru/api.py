from typing import Any, Dict, List

from base64 import b64encode
import re
from urllib.parse import urlencode, urlsplit, urlunsplit, urljoin

import requests


class FileToken:
    def __init__(self, token: str, filepath: str):
        self._token = token
        self._filepath = filepath

    @property
    def token(self):
        return self._token

    @property
    def filepath(self):
        return self._filepath

    def __str__(self) -> str:
        return f"<Upload token for file at {self._filepath}>"


class SzurubooruHTTPError(requests.exceptions.HTTPError):
    pass


class API:
    _token_checker = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    @staticmethod
    def _encode_auth_headers(u: str, p: str) -> str:
        return b64encode(f"{u}:{p}".encode("utf-8")).decode("ascii")

    @staticmethod
    def _check_api_response(r: requests.models.Response) -> None:
        if not r.status_code == requests.codes.ok:
            try:
                msg = r.json()
                msg = f"{msg['name']}: {msg['description']}"
            except ValueError:
                msg = r.text
            raise SzurubooruHTTPError(msg)

    def __init__(
        self,
        base_url: str,
        username: str = None,
        password: str = None,
        token: str = None,
        api_url: str = "api",
    ):
        # Extract Base URL parts
        parsed_base_url = urlsplit(base_url)
        self._url_scheme = parsed_base_url.scheme
        self._url_netloc = parsed_base_url.netloc
        if not (self._url_scheme and self._url_netloc):
            raise ValueError("Base URL is not valid")
        if self._url_scheme not in ("http", "https"):
            raise ValueError("Base URL must be of HTTP or HTTPS scheme")
        self._url_path_prefix = parsed_base_url.path.rstrip("/")

        # Extract API URL parts
        parsed_api_url = urlsplit(api_url)
        self._api_scheme = parsed_api_url.scheme or self._url_scheme
        self._api_netloc = parsed_api_url.netloc or self._url_netloc
        if self._api_scheme not in ("http", "https"):
            raise ValueError("API URL must be of HTTP or HTTPS scheme")
        if parsed_api_url.path.startswith("/") or self._api_netloc != self._url_netloc:
            self._api_path_prefix = parsed_api_url.path.rstrip("/")
        else:
            self._api_path_prefix = f"{self._url_path_prefix}/{parsed_api_url.path}".rstrip("/")

        # Extract Auth Info
        self._api_headers = {"Accept": "application/json"}
        username = username or parsed_api_url.username or parsed_base_url.username
        password = password or parsed_api_url.password or parsed_base_url.password
        if token:
            if not username:
                raise ValueError("Token authentication specified without username")
            if not self._token_checker.match(token):
                raise ValueError("Malformed Token String")
            self._api_headers["Authorization"] = f"Token {self._encode_auth_headers(username, token)}"
        elif password:
            if not username:
                raise ValueError("Password authentication specified without username")
            self._api_headers["Authorization"] = f"Basic {self._encode_auth_headers(username, password)}"
        elif username:
            raise ValueError("Username specified without authentication method")

    def _create_api_url(self, parts: List[str], query: Dict[str, str] = None) -> str:
        path = [self._api_path_prefix] + [str(part).rstrip("/") for part in parts]
        if query:
            path.append("")
            query = urlencode(query)
        return urlunsplit((self._api_scheme, self._api_netloc, "/".join(path), query, None))

    def _call(
        self, method: str, urlparts: List[str], urlquery: Dict[str, str] = None, body: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        req_kwargs = {"headers": self._api_headers}
        if body:
            req_kwargs["json"] = body
        response = requests.request(method, self._create_api_url(urlparts, urlquery), **req_kwargs)
        self._check_api_response(response)
        return response.json()

    def upload_file(self, filepath: str) -> FileToken:
        with open(filepath, "rb") as file:
            response = requests.post(
                self._create_api_url(["uploads"]),
                files={"content": file},
                headers=self._api_headers,
            )
        self._check_api_response(response)
        return FileToken(response.json()["token"], filepath)

    def _create_data_url(self, rel_url: str) -> str:
        base_url = urlunsplit((self._url_scheme, self._url_netloc, self._url_path_prefix, None, None))
        return urljoin(base_url, rel_url)
