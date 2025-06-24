"""middleware condition"""

import json
import random
import string

from fastapi import Request

def get_client_ip(request: Request) -> str:
    """get client ip"""
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host
    return client_ip

async def get_name(request: Request) -> str:
    """get name user"""
    body = await request.body()
    body_str = dict(json.loads(body.decode("utf-8")))

    if "fullname" in list(body_str.keys()):
        return body_str["fullname"]
    else:
        return ""

def get_submit_id(request: Request) -> str:
    """get submit id"""
    submit_id = ""
    if "submitId" in list(request.query_params.keys()):
        submit_id = request.query_params["submitId"]
    else:
        submit_id = generate_random_string()

    return submit_id

def get_endpoint(request: Request) -> str:
    """get endpoint"""
    return request.url.path

def generate_random_string(length=5):
    """Gen submit id"""
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for _ in range(length))
