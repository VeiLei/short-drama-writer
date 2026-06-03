"""
Volcano Engine (火山引擎) AK/SK authentication helper.
Uses volcengine SDK for V4 signing.
"""
import os
from collections import OrderedDict
from volcengine.Credentials import Credentials
from volcengine.auth.SignerV4 import SignerV4


def sign_request(
    method: str,
    host: str,
    path: str,
    headers: dict,
    body: str,
    ak: str,
    sk: str,
    region: str,
    service: str,
    query: dict = None,
) -> dict:
    """
    Sign an HTTP request using Volcano Engine V4 signing.
    Returns headers with X-Date and Authorization added.
    """
    from urllib.parse import parse_qs
    from volcengine.base.Request import Request

    uri = path
    if query is None and '?' in path:
        uri, qs = path.split('?', 1)
        parsed = parse_qs(qs, keep_blank_values=True)
        query = OrderedDict((k, v[0] if len(v) == 1 else v) for k, v in parsed.items())

    req = Request()
    req.set_method(method)
    req.set_host(host)
    req.set_path(uri)
    req.set_headers(OrderedDict(headers))
    req.set_body(body)
    if query:
        req.set_query(query)

    creds = Credentials(ak=ak, sk=sk, region=region, service=service)
    SignerV4.sign(req, creds)

    return dict(req.headers)


def get_signed_headers(
    method: str,
    host: str,
    path: str,
    body: str = "",
    content_type: str = "application/json",
    ak: str = None,
    sk: str = None,
    region: str = None,
    service: str = None,
) -> dict:
    """
    Build headers with Volcano Engine V4 auth signature.
    """
    if ak is None:
        ak = os.getenv("VOLCENGINE_ACCESS_KEY", "")
    if sk is None:
        sk = os.getenv("VOLCENGINE_SECRET_KEY", "")
    if region is None:
        region = os.getenv("VOLCENGINE_REGION", "cn-north-1")

    base_headers = OrderedDict([
        ("Content-Type", content_type),
    ])

    return sign_request(method, host, path, base_headers, body, ak, sk, region, service)
