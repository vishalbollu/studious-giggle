import sys

from fastapi import FastAPI

version = f"{sys.version_info.major}.{sys.version_info.minor}"

app = FastAPI()

import asyncio
import aiohttp
import json
import time
import os

USERNAME = os.environ["ELEVATE_USERNAME"]
PASSWORD = os.environ["ELEVATE_PASSWORD"]

services = {
    "denial": {
        "name": "denial",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/denial/",
        "normalizer": {},
    },
    "intrusion": {
        "name": "intrusion",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/intrusion/",
        "normalizer": {},
    },
    "executable": {
        "name": "executable",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/executable/",
        "normalizer": {},
    },
    "misuse": {
        "name": "misuse",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/misuse/",
        "normalizer": {},
    },
    "unauthorized": {
        "name": "unauthorized",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/unauthorized/",
        "normalizer": {},
    },
    "probing": {
        "name": "probing",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/probing/",
        "normalizer": {},
    },
    "other": {
        "name": "other",
        "url": "https://incident-api.use1stag.elevatesecurity.io/incidents/other/",
        "normalizer": {},
    },
    "identities": {
        "name": "identities",
        "url": "https://incident-api.use1stag.elevatesecurity.io/identities",
        "normalizer": {},
    },
}


async def async_requester(session, service_def):
    try:
        print(service_def)
        print(service_def["url"])
        start = time.time()
        async with session.get(url=service_def["url"]) as response:
            print(response.status)
            resp = await response.json()
            print(f"{service_def['name']} {time.time()-start}")
            return (service_def["name"], resp)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(service_def["url"], e.__class__))
        return (service_def["name"], {})


async def parallel_requests(urls):
    async with aiohttp.ClientSession(
        auth=aiohttp.BasicAuth(USERNAME, password=PASSWORD)
    ) as session:
        ret = await asyncio.gather(
            *[async_requester(session, service_def) for _, service_def in services.items()]
        )
    return ret


@app.get("/incidents")
async def incidents():
    parallel_results = await parallel_requests(services)
    with open("/workspace/results.json", "w") as out_file:
        json.dump(parallel_results, out_file)
    merged_results = {name: results for name, results in parallel_results}
    with open("/workspace/merged.json", "w") as out_file:
        json.dump(merged_results, out_file)
    message = f"Hello world! From FastAPI running on Uvicorn with Gunicorn. Using Python {version}"
    return {"message": message}


@app.get("/healthz")
async def healthz():
    return "ok"
